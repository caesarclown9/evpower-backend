# OCPP 1.6 WebSocket сервер для тестов
import asyncio
from websockets.server import serve
from ocpp.v16 import ChargePoint as CP
from ocpp.routing import on
from ocpp.v16 import call_result
from ocpp_ws_server.redis_manager import redis_manager

class ChargePoint(CP):
    @on('BootNotification')
    async def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
        print(f"BootNotification from {self.id}: {charge_point_model}, {charge_point_vendor}")
        return call_result.BootNotificationPayload(
            current_time='2024-06-01T12:00:00Z',
            interval=10,
            status='Accepted'
        )

    @on('Heartbeat')
    async def on_heartbeat(self, **kwargs):
        from datetime import datetime
        print(f"Heartbeat from {self.id}")
        return call_result.HeartbeatPayload(current_time=datetime.utcnow().isoformat())

    @on('StartTransaction')
    async def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        from datetime import datetime
        print(f"StartTransaction from {self.id}: connector {connector_id}, id_tag {id_tag}, meter_start {meter_start}, timestamp {timestamp}")
        transaction = {
            "station_id": self.id,
            "type": "start",
            "connector_id": connector_id,
            "id_tag": id_tag,
            "meter_start": meter_start,
            "timestamp": timestamp,
            "created_at": datetime.utcnow().isoformat()
        }
        await redis_manager.add_transaction(self.id, transaction)
        return call_result.StartTransactionPayload(
            transaction_id=1,  # Можно доработать генерацию id
            id_tag_info={"status": "Accepted"}
        )

    @on('StopTransaction')
    async def on_stop_transaction(self, meter_stop, timestamp, transaction_id, id_tag, **kwargs):
        from datetime import datetime
        print(f"StopTransaction from {self.id}: meter_stop {meter_stop}, transaction_id {transaction_id}, id_tag {id_tag}, timestamp {timestamp}")
        transaction = {
            "station_id": self.id,
            "type": "stop",
            "transaction_id": transaction_id,
            "id_tag": id_tag,
            "meter_stop": meter_stop,
            "timestamp": timestamp,
            "created_at": datetime.utcnow().isoformat()
        }
        await redis_manager.add_transaction(self.id, transaction)
        return call_result.StopTransactionPayload(
            id_tag_info={"status": "Accepted"}
        )

async def handle_pubsub_commands(charge_point, station_id):
    async for command in redis_manager.listen_commands(station_id):
        print(f"Получена команда для {station_id}: {command}")
        # Пример: поддержка только RemoteStartTransaction
        if command.get("command") == "RemoteStartTransaction":
            payload = command.get("payload", {})
            response = await charge_point.call("RemoteStartTransaction", **payload)
            print(f"Ответ на RemoteStartTransaction: {response}")
        # TODO: добавить обработку других команд

async def handler(websocket):
    # Получаем cp_id из пути подключения
    cp_id = websocket.path.split('/')[-1]
    print(f"Новое подключение: {cp_id}")
    charge_point = ChargePoint(cp_id, websocket)
    await redis_manager.register_station(cp_id)
    pubsub_task = asyncio.create_task(handle_pubsub_commands(charge_point, cp_id))
    try:
        await charge_point.start()
    finally:
        pubsub_task.cancel()
        await redis_manager.unregister_station(cp_id)
        print(f"Станция отключена: {cp_id}")

async def main():
    async with serve(handler, "0.0.0.0", 8180, subprotocols=["ocpp1.6"]):
        print("======== Running on ws://0.0.0.0:8180/ws/{cp_id} ========")
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main()) 