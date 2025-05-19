from fastapi import APIRouter, Depends, status, Body, HTTPException, Query
from typing import List, Optional
from app.schemas.ocpp import (
    OCPPConnection, OCPPConnectionCreate,
    OCPPTransaction, OCPPTransactionCreate
)
from app.core.deps import get_current_user, require_role, get_db
from pydantic import BaseModel, Field
from app.schemas.user import UserCreateWithRole, UserOut
from app.crud.users import create_user_with_role
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import UserRole
from app.db.models.station import Station
from sqlalchemy import select
from ocpp_ws_server.redis_manager import redis_manager

router = APIRouter(prefix="/ocpp", tags=["ocpp"])

# --- Pydantic схемы для Swagger ---
class OCPPConnectionStatus(str):
    active = 'active'
    inactive = 'inactive'
    error = 'error'

class OCPPConnection(BaseModel):
    station_id: str = Field(..., example="DE-BERLIN-001")
    status: str = Field(..., example="active")
    last_heartbeat: Optional[str] = Field(None, example="2024-06-01T12:00:00Z")

class OCPPCommandRequest(BaseModel):
    station_id: str = Field(..., example="DE-BERLIN-001")
    command: str = Field(..., example="RemoteStartTransaction")
    payload: Optional[dict] = Field(None, example={"connectorId": 1})

class OCPPCommandResponse(BaseModel):
    status: str = Field(..., example="sent")
    station_id: str = Field(..., example="DE-BERLIN-001")
    command: str = Field(..., example="RemoteStartTransaction")
    result: Optional[dict] = Field(None, example={"status": "Accepted"})

async def get_user_station_ids(db: AsyncSession, user) -> list[str]:
    if user.role == UserRole.admin:
        result = await db.execute(select(Station.id).where(Station.admin_id == user.id))
        return [row[0] for row in result.all()]
    elif user.role == UserRole.operator:
        result = await db.execute(select(Station.id).where(Station.admin_id == user.admin_id))
        return [row[0] for row in result.all()]
    else:
        result = await db.execute(select(Station.id))
        return [row[0] for row in result.all()]

# --- Эндпоинты ---

@router.get("/connections", response_model=List[OCPPConnection], summary="Список подключённых станций")
async def list_ocpp_connections():
    station_ids = await redis_manager.get_stations()
    return [
        OCPPConnection(station_id=station_id, status="active", last_heartbeat=None)
        for station_id in station_ids
    ]

@router.post("/connections", response_model=OCPPConnection, status_code=status.HTTP_201_CREATED)
async def create_ocpp_connection(connection_in: OCPPConnectionCreate):
    raise HTTPException(status_code=501, detail="Создание соединения реализуется через WebSocket-клиент.")

@router.get("/transactions", summary="List Ocpp Transactions")
async def list_ocpp_transactions(station_id: Optional[str] = Query(None)):
    txs = await redis_manager.get_transactions(station_id)
    return txs

@router.post("/transactions", summary="Create Ocpp Transaction")
async def create_ocpp_transaction(transaction_in: OCPPTransactionCreate):
    # Публикуем команду StartTransaction через Redis
    await redis_manager.publish_command(transaction_in.connection_id, {
        "command": "RemoteStartTransaction",
        "payload": {
            "connectorId": 1  # Можно доработать передачу connectorId
        }
    })
    return {"status": "sent", "station_id": transaction_in.connection_id}

@router.post("/send_command", response_model=OCPPCommandResponse, summary="Отправить команду на станцию через OCPP")
async def send_command(request: OCPPCommandRequest):
    await redis_manager.publish_command(request.station_id, {
        "command": request.command,
        "payload": request.payload or {}
    })
    return OCPPCommandResponse(
        status="sent",
        station_id=request.station_id,
        command=request.command,
        result={"info": "Команда отправлена через Redis Pub/Sub. Ожидайте выполнения на станции."}
    )

@router.get("/status/{station_id}", response_model=OCPPConnection, summary="Статус конкретной станции")
async def get_station_status(station_id: str):
    station_ids = await redis_manager.get_stations()
    status = "active" if station_id in station_ids else "inactive"
    return OCPPConnection(station_id=station_id, status=status, last_heartbeat=None)

@router.post("/disconnect", summary="Отключить станцию от WebSocket")
async def disconnect_station(station_id: str = Body(..., example="DE-BERLIN-001")):
    # Публикуем команду на отключение станции через Redis
    await redis_manager.publish_command(station_id, {"command": "Disconnect"})
    return {"status": "disconnect_sent", "station_id": station_id}
