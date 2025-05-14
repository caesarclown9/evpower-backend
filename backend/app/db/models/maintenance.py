from sqlalchemy import Column, String, DateTime, Enum as SqlEnum, ForeignKey
from sqlalchemy.sql import func
import enum
import uuid
from app.db.base_class import Base
from datetime import datetime, timedelta

class MaintenanceStatus(str, enum.Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    completed = 'completed'
    cancelled = 'cancelled'

def kyrgyzstan_now():
    # UTC+6
    return (datetime.utcnow() + timedelta(hours=6)).strftime('%Y-%m-%d')

class Maintenance(Base):
    __tablename__ = 'maintenance'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String, ForeignKey('stations.id'), nullable=False)
    request_date = Column(String, nullable=True, default=kyrgyzstan_now)
    description = Column(String)
    assigned_to = Column(String)
    notes = Column(String)
    status = Column(SqlEnum(MaintenanceStatus), default=MaintenanceStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
