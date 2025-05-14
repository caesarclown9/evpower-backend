from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str  # JWT access token
    refresh_token: Optional[str] = None
    user: dict  # или User, если есть отдельная схема пользователя

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    token: str
    refresh_token: Optional[str] = None
