# OCPP WebSocket Test Server

Этот сервер предназначен для тестирования подключения зарядных станций по протоколу OCPP 1.6 через WebSocket.

## Установка

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

(Выполнять из директории backend)

## Запуск

```powershell
python .\ocpp_ws_server\server.py
```

## Подключение

- WebSocket URL: `ws://localhost:9000/ws/<station_id>`
- Можно использовать эмулятор зарядной станции или Postman (WebSocket).

## Пример теста через Postman

1. Создайте WebSocket-запрос на `ws://localhost:9000/ws/test-station-001`
2. Отправьте BootNotification (OCPP 1.6 JSON Frame):

```
[
  2,
  "123456",
  "BootNotification",
  {
    "chargePointModel": "TestModel",
    "chargePointVendor": "TestVendor"
  }
]
```

3. Получите ответ от сервера.

---

- Сервер не зависит от FastAPI и не мешает основному приложению.
- В дальнейшем можно расширить обработку сообщений и интеграцию с БД. 