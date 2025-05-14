from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime

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
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
