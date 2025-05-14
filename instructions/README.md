# README: Бэкенд на FastAPI для системы управления ЭЗС

---

## Оглавление
1. [Описание проекта](#описание-проекта)
2. [Архитектура и цели](#архитектура-и-цели)
3. [Общая структура API](#общая-структура-api)
4. [Принципы проектирования API](#принципы-проектирования-api)
5. [Аутентификация и безопасность](#аутентификация-и-безопасность)
6. [Схемы данных (components/schemas)](#схемы-данных-componentsschemas)
7. [Ресурсы и эндпоинты](#ресурсы-и-эндпоинты)
    - [7.1. Станции](#71-станции)
    - [7.2. Клиенты](#72-клиенты)
    - [7.3. Локации](#73-локации)
    - [7.4. Обслуживание](#74-обслуживание)
    - [7.5. Аутентификация](#75-аутентификация)
    - [7.6. Отчеты](#76-отчеты)
    - [7.7. OCPP](#77-ocpp)
8. [Примеры запросов и ответов](#примеры-запросов-и-ответов)
9. [Рекомендации и TODO](#рекомендации-и-todo)
10. [Инструкции по запуску и генерации](#инструкции-по-запуску-и-генерации)

---

## 1. Описание проекта

Данный проект — это серверная часть системы управления электрозарядными станциями (ЭЗС), клиентами, локациями и обслуживанием. Вся бизнес-логика и структура API описаны в спецификациях OpenAPI 3.0 (Swagger), что позволяет быстро реализовать backend на FastAPI (Python).

---

## 2. Архитектура и цели

- **Модульная архитектура**: каждый ресурс (станции, клиенты, локации, обслуживание, отчеты, OCPP) реализован отдельным модулем.
- **RESTful API**: четкое разделение ресурсов, CRUD-операции, использование HTTP-методов.
- **JWT-аутентификация**: все защищённые эндпоинты требуют передачи Bearer-токена.
- **OpenAPI-спецификация**: вся структура, параметры, схемы и ответы строго типизированы.
- **Масштабируемость**: API легко расширяется за счет модульной структуры.
- **Документированность**: каждый эндпоинт снабжен описанием, примерами, схемами ошибок.

---

## 3. Общая структура API

- **Станции** (`/stations`, `/stations/{station_id}`, `/stations/{station_id}/status`)
- **Клиенты** (`/clients`, `/clients/{client_id}`)
- **Локации** (`/locations`, `/locations/{location_id}`)
- **Обслуживание** (`/maintenance`, `/maintenance/{maintenance_id}`)
- **Аутентификация** (`/auth/login`, `/auth/refresh`)
- **Отчеты** (`/reports/usage`, `/reports/revenue`)
- **OCPP** (`/ocpp/connections`, `/ocpp/transactions`)

---

## 4. Принципы проектирования API

- **RESTful**: Четкое разделение ресурсов, CRUD-операции, использование HTTP-методов.
- **JWT-аутентификация**: Все защищённые эндпоинты требуют передачи Bearer-токена.
- **OpenAPI-спецификация**: Вся структура, параметры, схемы и ответы строго типизированы.
- **Масштабируемость**: API легко расширяется за счет модульной структуры (разделы, схемы, компоненты).
- **Документированность**: Каждый эндпоинт снабжен описанием, примерами, схемами ошибок.

---

## 5. Аутентификация и безопасность

- Используется JWT (BearerAuth).
- Для защищённых эндпоинтов требуется заголовок:
  `Authorization: Bearer <token>`
- Описаны стандартные ошибки: 401 (Unauthorized), 400 (BadRequest), 404 (NotFound).

---

## 6. Схемы данных (components/schemas)

Все Pydantic-схемы для всех ресурсов вынесены в отдельный файл: [schemas.md](./schemas.md)

---

## 7. Ресурсы и эндпоинты

### 7.1. Станции (`/stations`)

#### Назначение
Ресурс предназначен для управления электрозарядными станциями: создание, получение списка, получение/обновление/удаление по ID, изменение статуса.

#### Эндпоинты

- **GET `/stations`** — Получить список всех станций (фильтрация по статусу, локации)
- **POST `/stations`** — Добавить новую станцию
- **GET `/stations/{station_id}`** — Получить подробную информацию о станции
- **PUT `/stations/{station_id}`** — Обновить данные станции
- **DELETE `/stations/{station_id}`** — Удалить станцию
- **PUT `/stations/{station_id}/status`** — Изменить статус станции

#### Параметры и схемы

- **Query параметры для GET /stations:**
  - `status`: string (active, inactive, maintenance)
  - `location_id`: string

- **Path параметры:**
  - `station_id`: string

- **RequestBody для POST/PUT:**
  - StationCreate / StationUpdate (см. ниже)

- **RequestBody для PUT /stations/{station_id}/status:**
  - status: string (active, inactive, maintenance)
  - reason: string (опционально)

#### Схемы данных (Pydantic)

```python
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel

class StationStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'
    maintenance = 'maintenance'

class StationBase(BaseModel):
    serial_number: str
    model: str
    manufacturer: str
    location_id: str
    power_capacity: float
    connector_types: List[str]
    installation_date: Optional[str] = None  # YYYY-MM-DD
    firmware_version: Optional[str] = None

class StationCreate(StationBase):
    pass

class StationUpdate(BaseModel):
    serial_number: Optional[str]
    model: Optional[str]
    manufacturer: Optional[str]
    location_id: Optional[str]
    power_capacity: Optional[float]
    connector_types: Optional[List[str]]
    installation_date: Optional[str]
    firmware_version: Optional[str]
    status: Optional[StationStatus]

class Station(StationBase):
    id: str
    status: StationStatus

class StationStatusUpdate(BaseModel):
    status: StationStatus
    reason: Optional[str] = None
```

#### Примеры запросов и ответов

**POST /stations**
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

**PUT /stations/{station_id}/status**
```json
{
  "status": "maintenance",
  "reason": "Плановое обслуживание"
}
```

#### Рекомендации по реализации на FastAPI

- Использовать Pydantic-модели для описания схем Station, StationCreate, StationUpdate, StationStatusUpdate.
- Для фильтрации в GET-эндпоинтах использовать Query параметры FastAPI.
- Для статусов использовать Enum.
- Все защищённые эндпоинты должны требовать JWT-аутентификацию (Depends(get_current_user)).
- Для ошибок использовать стандартные HTTPException с нужным статусом и описанием.
- Для документации использовать docstring и аннотации FastAPI — OpenAPI будет генерироваться автоматически.

---

### 7.2. Клиенты (`/clients`)

#### Назначение
Ресурс предназначен для управления клиентами системы: создание, получение списка, получение/обновление/удаление по ID.

#### Эндпоинты

- **GET `/clients`** — Получить список всех клиентов (фильтрация по статусу)
- **POST `/clients`** — Добавить нового клиента
- **GET `/clients/{client_id}`** — Получить подробную информацию о клиенте
- **PUT `/clients/{client_id}`** — Обновить данные клиента
- **DELETE `/clients/{client_id}`** — Удалить клиента

#### Параметры и схемы

- **Query параметры для GET /clients:**
  - `status`: string (active, inactive, blocked)

- **Path параметры:**
  - `client_id`: string

- **RequestBody для POST/PUT:**
  - ClientCreate / ClientUpdate (см. ниже)

#### Схемы данных (Pydantic)

```python
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr

class ClientStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'
    blocked = 'blocked'

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    contract_number: Optional[str] = None
    contract_start_date: Optional[str] = None  # YYYY-MM-DD
    contract_end_date: Optional[str] = None    # YYYY-MM-DD

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    address: Optional[str]
    contract_number: Optional[str]
    contract_start_date: Optional[str]
    contract_end_date: Optional[str]
    status: Optional[ClientStatus]

class Client(ClientBase):
    id: str
    status: ClientStatus
    created_at: str  # date-time
    updated_at: str  # date-time
```

#### Примеры запросов и ответов

**POST /clients**
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

**PUT /clients/{client_id}**
```json
{
  "phone": "+7-999-765-43-21",
  "status": "inactive"
}
```

#### Рекомендации по реализации на FastAPI

- Использовать Pydantic-модели для описания схем Client, ClientCreate, ClientUpdate.
- Для фильтрации в GET-эндпоинтах использовать Query параметры FastAPI.
- Для статусов использовать Enum.
- Все защищённые эндпоинты должны требовать JWT-аутентификацию (Depends(get_current_user)).
- Для ошибок использовать стандартные HTTPException с нужным статусом и описанием.
- Для документации использовать docstring и аннотации FastAPI — OpenAPI будет генерироваться автоматически.

---

### 7.3. Локации (`/locations`)

#### Назначение
Ресурс предназначен для управления локациями зарядных станций: создание, получение списка, получение/обновление/удаление по ID.

#### Эндпоинты

- **GET `/locations`** — Получить список всех локаций (фильтрация по статусу)
- **POST `/locations`** — Добавить новую локацию
- **GET `/locations/{location_id}`** — Получить подробную информацию о локации
- **PUT `/locations/{location_id}`** — Обновить данные локации
- **DELETE `/locations/{location_id}`** — Удалить локацию

#### Параметры и схемы

- **Query параметры для GET /locations:**
  - `status`: string (active, inactive, under_construction)

- **Path параметры:**
  - `location_id`: string

- **RequestBody для POST/PUT:**
  - LocationCreate / LocationUpdate (см. ниже)

#### Схемы данных (Pydantic)

```python
from typing import Optional
from enum import Enum
from pydantic import BaseModel

class LocationStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'
    under_construction = 'under_construction'

class LocationBase(BaseModel):
    name: str
    address: str
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    client_id: Optional[str] = None
    working_hours: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    city: Optional[str]
    region: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    client_id: Optional[str]
    working_hours: Optional[str]
    status: Optional[LocationStatus]

class Location(LocationBase):
    id: str
    status: LocationStatus
```

#### Примеры запросов и ответов

**POST /locations**
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

**PUT /locations/{location_id}**
```json
{
  "working_hours": "09:00-22:00",
  "status": "inactive"
}
```

#### Рекомендации по реализации на FastAPI

- Использовать Pydantic-модели для описания схем Location, LocationCreate, LocationUpdate.
- Для фильтрации в GET-эндпоинтах использовать Query параметры FastAPI.
- Для статусов использовать Enum.
- Все защищённые эндпоинты должны требовать JWT-аутентификацию (Depends(get_current_user)).
- Для ошибок использовать стандартные HTTPException с нужным статусом и описанием.
- Для документации использовать docstring и аннотации FastAPI — OpenAPI будет генерироваться автоматически.

---

### 7.4. Обслуживание (`/maintenance`)

#### Назначение
Ресурс предназначен для управления заявками на обслуживание зарядных станций: создание, получение списка, получение/обновление/удаление по ID.

#### Эндпоинты

- **GET `/maintenance`** — Получить список всех заявок на обслуживание (фильтрация по статусу, станции, дате)
- **POST `/maintenance`** — Создать новую заявку на обслуживание
- **GET `/maintenance/{maintenance_id}`** — Получить подробную информацию о заявке
- **PUT `/maintenance/{maintenance_id}`** — Обновить данные заявки
- **DELETE `/maintenance/{maintenance_id}`** — Удалить заявку

#### Параметры и схемы

- **Query параметры для GET /maintenance:**
  - `status`: string (pending, in_progress, completed, cancelled)
  - `station_id`: string
  - `start_date`: string (YYYY-MM-DD)
  - `end_date`: string (YYYY-MM-DD)

- **Path параметры:**
  - `maintenance_id`: string

- **RequestBody для POST/PUT:**
  - MaintenanceCreate / MaintenanceUpdate (см. ниже)

#### Схемы данных (Pydantic)

```python
from typing import Optional
from enum import Enum
from pydantic import BaseModel

class MaintenanceStatus(str, Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    completed = 'completed'
    cancelled = 'cancelled'

class MaintenanceBase(BaseModel):
    station_id: str
    request_date: Optional[str] = None  # YYYY-MM-DD
    description: Optional[str] = None
    assigned_to: Optional[str] = None  # ID пользователя/техника
    notes: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    description: Optional[str]
    assigned_to: Optional[str]
    notes: Optional[str]
    status: Optional[MaintenanceStatus]

class MaintenanceRequest(MaintenanceBase):
    id: str
    status: MaintenanceStatus
    created_at: str  # date-time
    updated_at: str  # date-time
```

#### Примеры запросов и ответов

**POST /maintenance**
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

**PUT /maintenance/{maintenance_id}**
```json
{
  "status": "completed",
  "notes": "Проведена замена разъема, станция работает штатно."
}
```

#### Рекомендации по реализации на FastAPI

- Использовать Pydantic-модели для описания схем MaintenanceRequest, MaintenanceCreate, MaintenanceUpdate.
- Для фильтрации в GET-эндпоинтах использовать Query параметры FastAPI.
- Для статусов использовать Enum.
- Все защищённые эндпоинты должны требовать JWT-аутентификацию (Depends(get_current_user)).
- Для ошибок использовать стандартные HTTPException с нужным статусом и описанием.
- Для документации использовать docstring и аннотации FastAPI — OpenAPI будет генерироваться автоматически.

---

### 7.5. Аутентификация (`/auth`)

#### Назначение
Ресурс предназначен для аутентификации пользователей системы: вход, обновление токена, выход.

#### Эндпоинты

- **POST `/auth/login`** — Вход в систему, получение JWT-токена
- **POST `/auth/refresh`** — Обновление JWT-токена
- **POST `/auth/logout`** — Выход из системы (опционально, если реализовано)

#### Параметры и схемы

- **RequestBody для POST /auth/login:**
  - email: string (email)
  - password: string

- **RequestBody для POST /auth/refresh:**
  - refresh_token: string

#### Схемы данных (Pydantic)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str  # JWT access token
    refresh_token: Optional[str] = None
    user: dict  # или User, если есть отдельная схема пользователя

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    token: str
    refresh_token: Optional[str] = None
```

#### Примеры запросов и ответов

**POST /auth/login**
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

**POST /auth/refresh**
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

#### Рекомендации по реализации на FastAPI

- Использовать Pydantic-модели для описания схем LoginRequest, LoginResponse, RefreshRequest, RefreshResponse.
- Для аутентификации использовать стандартные подходы FastAPI (OAuth2PasswordBearer, JWT).
- Для хранения refresh-токенов использовать отдельную таблицу или Redis (по необходимости).
- Для ошибок использовать стандартные HTTPException с нужным статусом и описанием (401 Unauthorized при неверных данных).
- Для документации использовать docstring и аннотации FastAPI — OpenAPI будет генерироваться автоматически.

---

### 7.6. Отчеты (`/reports`)

#### Назначение
Ресурс предназначен для получения отчетов о работе системы: использование электроэнергии, доходы.

#### Эндпоинты

- **GET `/reports/usage`** — Получить отчет о работе системы
- **GET `/reports/revenue`** — Получить отчет о доходах системы

#### Параметры и схемы

- **Query параметры для GET /reports/usage:**
  - `start_date`: string (YYYY-MM-DD)
  - `end_date`: string (YYYY-MM-DD)

- **Query параметры для GET /reports/revenue:**
  - `start_date`: string (YYYY-MM-DD)
  - `end_date`: string (YYYY-MM-DD)

#### Схемы данных (Pydantic)

```python
from typing import Optional
from pydantic import BaseModel

class UsageReport(BaseModel):
    station_id: str
    usage: float  # kWh
    date: str  # date-time

class RevenueReport(BaseModel):
    revenue: float  # RUB
    date: str  # date-time
```

#### Примеры запросов и ответов

**GET /reports/usage**
```json
{
  "usage": 123.45,
  "date": "2024-05-01T10:00:00Z"
}
```

**GET /reports/revenue**
```json
{
  "revenue": 12345.67,
  "date": "2024-05-01T10:00:00Z"
}
```

#### Рекомендации по реализации на FastAPI

- Использовать Pydantic-модели для описания схем UsageReport, RevenueReport.
- Для фильтрации в GET-эндпоинтах использовать Query параметры FastAPI.
- Для ошибок использовать стандартные HTTPException с нужным статусом и описанием.
- Для документации использовать docstring и аннотации FastAPI — OpenAPI будет генерироваться автоматически.

---

### 7.7. OCPP (`/ocpp`)

#### Назначение
Ресурс предназначен для управления взаимодействием с зарядными станциями по протоколу OCPP: управление соединениями, транзакциями, мониторинг.

#### Эндпоинты

- **GET `/ocpp/connections`** — Получить список OCPP-соединений
- **POST `/ocpp/connections`** — Создать новое OCPP-соединение
- **GET `/ocpp/transactions`** — Получить список OCPP-транзакций
- **POST `/ocpp/transactions`** — Создать новую OCPP-транзакцию

#### Параметры и схемы

- **Query параметры для GET /ocpp/connections:**
  - `status`: string (active, inactive, error)
  - `station_id`: string

- **RequestBody для POST /ocpp/connections:**
  - OCPPConnectionCreate (см. ниже)

- **RequestBody для POST /ocpp/transactions:**
  - OCPPTransactionCreate (см. ниже)

#### Схемы данных (Pydantic)

```python
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel

class OCPPConnectionStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'
    error = 'error'

class OCPPConnectionBase(BaseModel):
    station_id: str
    status: OCPPConnectionStatus
    last_heartbeat: Optional[str] = None  # date-time

class OCPPConnectionCreate(BaseModel):
    station_id: str

class OCPPConnection(OCPPConnectionBase):
    id: str

class OCPPTransactionStatus(str, Enum):
    started = 'started'
    stopped = 'stopped'
    error = 'error'

class OCPPTransactionBase(BaseModel):
    connection_id: str
    start_time: str  # date-time
    stop_time: Optional[str] = None  # date-time
    energy: Optional[float] = None  # kWh
    status: OCPPTransactionStatus

class OCPPTransactionCreate(BaseModel):
    connection_id: str
    start_time: str

class OCPPTransaction(OCPPTransactionBase):
    id: str
```

#### Примеры запросов и ответов

**POST /ocpp/connections**
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

**POST /ocpp/transactions**
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

#### Рекомендации по реализации на FastAPI

- Использовать Pydantic-модели для описания схем OCPPConnection, OCPPConnectionCreate, OCPPTransaction, OCPPTransactionCreate.
- Для фильтрации в GET-эндпоинтах использовать Query параметры FastAPI.
- Для статусов использовать Enum.
- Все защищённые эндпоинты должны требовать JWT-аутентификацию (Depends(get_current_user)).
- Для ошибок использовать стандартные HTTPException с нужным статусом и описанием.
- Для документации использовать docstring и аннотации FastAPI — OpenAPI будет генерироваться автоматически.

---

## 8. Примеры запросов и ответов

Все примеры вынесены в отдельный файл: [examples.md](./examples.md)

---

## 9. Рекомендации и TODO

- Проверить актуальность всех схем и примеров.
- Добавить примеры ошибок и успешных ответов для всех эндпоинтов.
- Реализовать тесты для всех маршрутов (unit, integration, e2e).
- Продумать миграции и структуру БД на основе схем.
- Реализовать автоматическую генерацию документации на основе OpenAPI.
- Настроить CI/CD для автоматического тестирования и деплоя.
- Подготовить .env.example и инструкции по настройке переменных окружения.
- Добавить Postman-коллекцию для ручного тестирования API.

---

## 10. Инструкции по запуску и генерации

(Будут добавлены после формирования структуры FastAPI-проекта. Включат инструкции по установке зависимостей, запуску сервера, генерации моделей из OpenAPI, настройке переменных окружения, запуску тестов и CI/CD.)

---

> Документ формируется на основе спецификаций OpenAPI/Swagger и всей документации проекта. Следующие разделы содержат подробное описание каждого ресурса, схемы, примеры и рекомендации по реализации на FastAPI. 