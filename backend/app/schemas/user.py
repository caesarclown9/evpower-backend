from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    operator = 'operator'
    admin = 'admin'
    superadmin = 'superadmin'

class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    role: UserRole = UserRole.operator

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserCreateWithRole(UserCreate):
    role: UserRole

class UserOut(UserBase):
    id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True) 