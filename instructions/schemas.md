# Схемы данных (Pydantic models)

## Станции
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

## Клиенты
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

## Локации
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

## Обслуживание
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

## Аутентификация
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

## Отчеты
```python
from pydantic import BaseModel

class UsageReport(BaseModel):
    station_id: str
    usage: float  # kWh
    date: str  # date-time

class RevenueReport(BaseModel):
    revenue: float  # RUB
    date: str  # date-time
```

## OCPP
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