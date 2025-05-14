from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MaintenanceStatus(str, Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    completed = 'completed'
    cancelled = 'cancelled'

class MaintenanceBase(BaseModel):
    station_id: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None  # ID пользователя/техника
    notes: Optional[str] = None
    request_date: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    description: Optional[str]
    assigned_to: Optional[str]
    notes: Optional[str]
    status: Optional[MaintenanceStatus]
    request_date: Optional[str] = None

class MaintenanceRequest(MaintenanceBase):
    id: str
    status: MaintenanceStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
