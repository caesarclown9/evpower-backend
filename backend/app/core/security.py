from passlib.context import CryptContext
from pydantic import BaseModel
import os
import jwt
from datetime import datetime, timedelta
from typing import Any, Optional

# Хэширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None, extra: dict = None) -> str:
    to_encode = {"sub": subject, "iat": datetime.utcnow()}
    if extra:
        to_encode.update(extra)
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Any:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# JWT настройки
class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
    authjwt_algorithm: str = ALGORITHM
    authjwt_access_token_expires: int = ACCESS_TOKEN_EXPIRE_MINUTES
