import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from app.api import auth, clients, stations, locations, ocpp
from fastapi.middleware.cors import CORSMiddleware
import logging
from ocpp.v16 import ChargePoint as CP
from ocpp.routing import on
from ocpp.v16 import call_result
from ocpp_ws_server.redis_manager import redis_manager
from app.db.session import SessionLocal
from app.crud.ocpp import get_charging_session, update_charging_session, list_tariffs
from app.crud.users import get_user_by_id, update_user
from datetime import datetime
import asyncio

# --- Импорт для автоматического создания полей ---
from app.db.base_class import Base
from app.db.session import engine
from app.db import models  # noqa: F401, чтобы зарегистрировать все модели

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI(title="EV Power Backend API", version="1.0.0")

# --- Кастомизация OpenAPI для поддержки Bearer Auth ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # По умолчанию требовать авторизацию для всех эндпоинтов (можно убрать если не нужно)
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS (разрешить всё для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(stations.router)
app.include_router(locations.router)
app.include_router(ocpp.router)

# TODO: добавить остальные роутеры (locations, maintenance, reports, ocpp)

# --- Автоматическое создание полей в таблицах ---
@app.on_event("startup")
def on_startup():
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)

# --- Хранилище активных сессий и лимитов (in-memory, можно заменить на Redis) ---
active_sessions = {}  # station_id: {session_id, energy_limit, energy_delivered}

class ChargePoint(CP):
    @on('BootNotification')
    def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
        print(f"BootNotification from {self.id}: {charge_point_model}, {charge_point_vendor}")
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat() + 'Z',
            interval=10,
            status='Accepted'
        )

    @on('Heartbeat')
    def on_heartbeat(self, **kwargs):
        print(f"Heartbeat from {self.id}")
        return call_result.HeartbeatPayload(current_time=datetime.utcnow().isoformat())

    @on('StartTransaction')
    def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        print(f"StartTransaction from {self.id}: connector {connector_id}, id_tag {id_tag}, meter_start {meter_start}, timestamp {timestamp}")
        session = active_sessions.get(self.id, {})
        session['meter_start'] = meter_start
        session['energy_delivered'] = 0.0
        transaction_id = int(datetime.utcnow().timestamp())
        session['transaction_id'] = transaction_id
        active_sessions[self.id] = session
        transaction = {
            "station_id": self.id,
            "type": "start",
            "connector_id": connector_id,
            "id_tag": id_tag,
            "meter_start": meter_start,
            "timestamp": timestamp,
            "created_at": datetime.utcnow().isoformat(),
            "transaction_id": transaction_id
        }
        # TODO: если нужно, реализовать sync-логику для Redis
        return call_result.StartTransactionPayload(
            transaction_id=transaction_id,
            id_tag_info={"status": "Accepted"}
        )

    @on('StopTransaction')
    def on_stop_transaction(self, meter_stop, timestamp, transaction_id, id_tag, **kwargs):
        print(f"StopTransaction from {self.id}: meter_stop {meter_stop}, transaction_id {transaction_id}, id_tag {id_tag}, timestamp {timestamp}")
        session_info = active_sessions.get(self.id)
        if self.id in active_sessions:
            del active_sessions[self.id]
        transaction = {
            "station_id": self.id,
            "type": "stop",
            "transaction_id": transaction_id,
            "id_tag": id_tag,
            "meter_stop": meter_stop,
            "timestamp": timestamp,
            "created_at": datetime.utcnow().isoformat()
        }
        # TODO: если нужно, реализовать sync-логику для Redis
        if session_info and session_info.get('session_id'):
            session_id = session_info['session_id']
            try:
                db = SessionLocal()
                charging_session = get_charging_session(db, session_id)
                if charging_session:
                    meter_start = session_info.get('meter_start', 0.0)
                    energy_delivered = float(meter_stop) - float(meter_start)
                    tariffs = list_tariffs(db, charging_session.station_id)
                    tariff = tariffs[0] if tariffs else None
                    amount = energy_delivered * tariff.price_per_kwh if tariff else 0.0
                    user = get_user_by_id(db, charging_session.user_id)
                    if user and user.balance >= amount:
                        update_charging_session(db, session_id, {
                            'energy': energy_delivered,
                            'amount': amount,
                            'status': 'stopped',
                            'stop_time': datetime.utcnow()
                        })
                        user.balance -= amount
                        db.commit()
                    else:
                        update_charging_session(db, session_id, {
                            'energy': energy_delivered,
                            'amount': amount,
                            'status': 'error',
                            'stop_time': datetime.utcnow()
                        })
                        db.commit()
            except Exception as e:
                print(f"[DB ERROR] Ошибка при обновлении ChargingSession/баланса: {e}")
            finally:
                db.close()
        return call_result.StopTransactionPayload(
            id_tag_info={"status": "Accepted"}
        )

    @on('MeterValues')
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        print(f"MeterValues from {self.id}: {meter_value}")
        session = active_sessions.get(self.id)
        if not session:
            return
        try:
            value = meter_value[0]['sampledValue'][0]['value']
            value = float(value)
        except Exception:
            return
        meter_start = session.get('meter_start', 0.0)
        energy_delivered = value - meter_start
        session['energy_delivered'] = energy_delivered
        energy_limit = session.get('energy_limit')
        if energy_limit and energy_delivered >= energy_limit:
            print(f"Достигнут лимит энергии {energy_delivered} >= {energy_limit}, инициируем StopTransaction!")
            await redis_manager.publish_command(self.id, {"command": "RemoteStopTransaction"})
        active_sessions[self.id] = session

async def handle_pubsub_commands(charge_point, station_id):
    async for command in redis_manager.listen_commands(station_id):
        print(f"Получена команда для {station_id}: {command}")
        if command.get("command") == "RemoteStartTransaction":
            payload = command.get("payload", {})
            session_id = payload.get("session_id")
            energy_limit = payload.get("energy_limit")
            active_sessions[station_id] = {
                "session_id": session_id,
                "energy_limit": energy_limit,
                "energy_delivered": 0.0
            }
            response = await charge_point.call("RemoteStartTransaction", **payload)
            print(f"Ответ на RemoteStartTransaction: {response}")
        elif command.get("command") == "RemoteStopTransaction":
            print(f"RemoteStopTransaction для {station_id}")
            session = active_sessions.get(station_id, {})
            transaction_id = session.get('transaction_id', 1)
            await charge_point.call("StopTransaction", transaction_id=transaction_id, meter_stop=0, timestamp=datetime.utcnow().isoformat(), id_tag="system")

@app.websocket("/ws/{station_id}")
async def ocpp_ws(websocket: WebSocket, station_id: str):
    await websocket.accept(subprotocol="ocpp1.6")
    charge_point = ChargePoint(station_id, websocket)
    await redis_manager.register_station(station_id)
    pubsub_task = asyncio.create_task(handle_pubsub_commands(charge_point, station_id))
    try:
        await charge_point.start()
    except WebSocketDisconnect:
        print(f"WebSocketDisconnect: {station_id}")
    finally:
        pubsub_task.cancel()
        await redis_manager.unregister_station(station_id)
        print(f"Станция отключена: {station_id}")

