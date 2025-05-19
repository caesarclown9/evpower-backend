from sqlalchemy import Column, String, Boolean, DateTime, Enum as SqlEnum
from sqlalchemy.sql import func
import enum
import uuid
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    operator = 'operator'
    admin = 'admin'
    superadmin = 'superadmin'

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SqlEnum(UserRole), default=UserRole.operator, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    admin_id = Column(String, nullable=True)  # Для operator — id admin, для других ролей — None
