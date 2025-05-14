from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime

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
    firmware_version: Optional[str] = None
    installation_date: Optional[str] = None

class StationCreate(StationBase):
    pass

class StationUpdate(BaseModel):
    serial_number: Optional[str]
    model: Optional[str]
    manufacturer: Optional[str]
    location_id: Optional[str]
    power_capacity: Optional[float]
    connector_types: Optional[List[str]]
    firmware_version: Optional[str]
    installation_date: Optional[str] = None
    status: Optional[StationStatus]

class Station(StationBase):
    id: str
    status: StationStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class StationStatusUpdate(BaseModel):
    status: StationStatus
    reason: Optional[str] = None
