# Примеры запросов и ответов

## Станции

### POST /stations
**Запрос:**
```json
{
  "serial_number": "SN-123456",
  "model": "EVX-1000",
  "manufacturer": "ElectroCorp",
  "location_id": "loc-001",
  "power_capacity": 22,
  "connector_types": ["Type2", "CCS"],
  "installation_date": "2024-01-15",
  "firmware_version": "1.2.3"
}
```
**Ответ:**
```json
{
  "id": "station-001",
  "serial_number": "SN-123456",
  "model": "EVX-1000",
  "manufacturer": "ElectroCorp",
  "location_id": "loc-001",
  "status": "active",
  "power_capacity": 22,
  "connector_types": ["Type2", "CCS"],
  "installation_date": "2024-01-15",
  "firmware_version": "1.2.3"
}
```

### PUT /stations/{station_id}/status
**Запрос:**
```json
{
  "status": "maintenance",
  "reason": "Плановое обслуживание"
}
```

---

## Клиенты

### POST /clients
**Запрос:**
```json
{
  "name": "ООО ЭлектроПлюс",
  "email": "client@electroplus.ru",
  "phone": "+7-999-123-45-67",
  "address": "г. Москва, ул. Примерная, д. 1",
  "contract_number": "C-2024-001",
  "contract_start_date": "2024-01-01",
  "contract_end_date": "2025-01-01"
}
```
**Ответ:**
```json
{
  "id": "client-001",
  "name": "ООО ЭлектроПлюс",
  "email": "client@electroplus.ru",
  "phone": "+7-999-123-45-67",
  "address": "г. Москва, ул. Примерная, д. 1",
  "contract_number": "C-2024-001",
  "contract_start_date": "2024-01-01",
  "contract_end_date": "2025-01-01",
  "status": "active",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### PUT /clients/{client_id}
**Запрос:**
```json
{
  "phone": "+7-999-765-43-21",
  "status": "inactive"
}
```

---

## Локации

### POST /locations
**Запрос:**
```json
{
  "name": "ТРЦ Мега",
  "address": "г. Москва, пр-т Вернадского, 6",
  "city": "Москва",
  "region": "Москва",
  "postal_code": "119526",
  "country": "Россия",
  "latitude": 55.6761,
  "longitude": 37.5046,
  "client_id": "client-001",
  "working_hours": "08:00-23:00"
}
```
**Ответ:**
```json
{
  "id": "loc-001",
  "name": "ТРЦ Мега",
  "address": "г. Москва, пр-т Вернадского, 6",
  "city": "Москва",
  "region": "Москва",
  "postal_code": "119526",
  "country": "Россия",
  "latitude": 55.6761,
  "longitude": 37.5046,
  "client_id": "client-001",
  "working_hours": "08:00-23:00",
  "status": "active"
}
```

### PUT /locations/{location_id}
**Запрос:**
```json
{
  "working_hours": "09:00-22:00",
  "status": "inactive"
}
```

---

## Обслуживание

### POST /maintenance
**Запрос:**
```json
{
  "station_id": "station-001",
  "request_date": "2024-05-01",
  "description": "Неисправность разъема Type2",
  "assigned_to": "user-002"
}
```
**Ответ:**
```json
{
  "id": "mnt-001",
  "station_id": "station-001",
  "request_date": "2024-05-01",
  "description": "Неисправность разъема Type2",
  "assigned_to": "user-002",
  "notes": null,
  "status": "pending",
  "created_at": "2024-05-01T09:00:00Z",
  "updated_at": "2024-05-01T09:00:00Z"
}
```

### PUT /maintenance/{maintenance_id}
**Запрос:**
```json
{
  "status": "completed",
  "notes": "Проведена замена разъема, станция работает штатно."
}
```

---

## Аутентификация

### POST /auth/login
**Запрос:**
```json
{
  "email": "admin@ezs-system.com",
  "password": "secret123"
}
```
**Ответ:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "user": {
    "id": "user-001",
    "email": "admin@ezs-system.com",
    "role": "admin"
  }
}
```

### POST /auth/refresh
**Запрос:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
}
```
**Ответ:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
}
```

---

## Отчеты

### GET /reports/usage
**Ответ:**
```json
{
  "usage": 123.45,
  "date": "2024-05-01T10:00:00Z"
}
```

### GET /reports/revenue
**Ответ:**
```json
{
  "revenue": 12345.67,
  "date": "2024-05-01T10:00:00Z"
}
```

---

## OCPP

### POST /ocpp/connections
**Запрос:**
```json
{
  "station_id": "station-001"
}
```
**Ответ:**
```json
{
  "id": "ocpp-conn-001",
  "station_id": "station-001",
  "status": "active",
  "last_heartbeat": "2024-05-01T10:00:00Z"
}
```

### POST /ocpp/transactions
**Запрос:**
```json
{
  "connection_id": "ocpp-conn-001",
  "start_time": "2024-05-01T10:00:00Z"
}
```
**Ответ:**
```json
{
  "id": "ocpp-trx-001",
  "connection_id": "ocpp-conn-001",
  "start_time": "2024-05-01T10:00:00Z",
  "status": "started"
}
``` 