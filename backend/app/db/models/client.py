from sqlalchemy import Column, String, Boolean, DateTime, Enum as SqlEnum, Date
from sqlalchemy.sql import func
import enum
import uuid
from app.db.base_class import Base
from datetime import datetime, timedelta

class ClientStatus(str, enum.Enum):
    active = 'active'
    inactive = 'inactive'
    blocked = 'blocked'

def kyrgyzstan_now():
    # UTC+6
    return (datetime.utcnow() + timedelta(hours=6)).date()

class Client(Base):
    __tablename__ = 'clients'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    address = Column(String)
    contract_number = Column(String)
    contract_start_date = Column(Date, nullable=True, default=kyrgyzstan_now)
    contract_end_date = Column(Date, nullable=True)
    status = Column(SqlEnum(ClientStatus), default=ClientStatus.active, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
