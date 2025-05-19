from sqlalchemy import Column, String, Float, DateTime, Enum as SqlEnum, ForeignKey, ARRAY
from sqlalchemy.sql import func
import enum
import uuid
from app.db.base_class import Base
from datetime import datetime, timedelta

class StationStatus(str, enum.Enum):
    active = 'active'
    inactive = 'inactive'
    maintenance = 'maintenance'

def kyrgyzstan_now():
    # UTC+6
    return (datetime.utcnow() + timedelta(hours=6)).strftime('%Y-%m-%d')

class Station(Base):
    __tablename__ = 'stations'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    serial_number = Column(String, unique=True, nullable=False)
    model = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    location_id = Column(String, ForeignKey('locations.id'), nullable=False)
    power_capacity = Column(Float, nullable=False)
    connector_types = Column(ARRAY(String), nullable=False)
    installation_date = Column(String, nullable=True, default=kyrgyzstan_now)
    firmware_version = Column(String)
    status = Column(SqlEnum(StationStatus), default=StationStatus.active, nullable=False)
    admin_id = Column(String, nullable=False)  # Владелец станции (admin/operator)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
