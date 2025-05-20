from sqlalchemy import Column, String, Float, DateTime, Enum as SqlEnum
from sqlalchemy.sql import func
import enum
import uuid
from app.db.base_class import Base

class LocationStatus(str, enum.Enum):
    active = 'active'
    inactive = 'inactive'
    under_construction = 'under_construction'

class Location(Base):
    __tablename__ = 'locations'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String)
    region = Column(String)
    postal_code = Column(String)
    country = Column(String)
    latitude = Column(Float)
    longitude = Column(Float, nullable=True)
    geo_point = Column(String, nullable=True)
    client_id = Column(String)
    working_hours = Column(String)
    status = Column(SqlEnum(LocationStatus), default=LocationStatus.active, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
