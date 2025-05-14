from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class OCPPConnectionStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'
    error = 'error'

class OCPPConnectionBase(BaseModel):
    station_id: str
    status: OCPPConnectionStatus

class OCPPConnectionCreate(BaseModel):
    station_id: str

class OCPPConnection(OCPPConnectionBase):
    id: str
    last_heartbeat: Optional[datetime] = None  # Только для вывода
    model_config = ConfigDict(from_attributes=True)

class OCPPTransactionStatus(str, Enum):
    started = 'started'
    stopped = 'stopped'
    error = 'error'

class OCPPTransactionBase(BaseModel):
    connection_id: str
    energy: Optional[float] = None  # kWh
    status: OCPPTransactionStatus

class OCPPTransactionCreate(BaseModel):
    connection_id: str

class OCPPTransaction(OCPPTransactionBase):
    id: str
    start_time: Optional[datetime] = None  # Только для вывода
    stop_time: Optional[datetime] = None  # Только для вывода
    model_config = ConfigDict(from_attributes=True)
