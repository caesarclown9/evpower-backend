from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date, datetime

class ClientStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'
    blocked = 'blocked'

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    contract_number: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    status: Optional[ClientStatus] = ClientStatus.active

class ClientCreate(ClientBase):
    password: str

class ClientLogin(BaseModel):
    email: EmailStr
    password: str

class ClientOut(ClientBase):
    id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contract_number: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    status: Optional[ClientStatus] = None
    # TODO: добавить дополнительные поля профиля

class ClientChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ClientForgotPasswordRequest(BaseModel):
    email: EmailStr

class ClientResetPasswordRequest(BaseModel):
    token: str
    new_password: str
