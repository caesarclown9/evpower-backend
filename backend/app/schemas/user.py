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
    admin_id: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserCreateWithRole(UserCreate):
    role: UserRole
    admin_id: Optional[str] = None

class UserOut(UserBase):
    id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    admin_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    admin_id: Optional[str] = None
    # Можно добавить другие поля профиля, если потребуется
    # TODO: добавить дополнительные поля профиля

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str 