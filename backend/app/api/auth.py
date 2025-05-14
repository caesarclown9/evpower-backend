from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserOut
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, RefreshResponse
from app.crud import users as crud_users
from app.core.security import verify_password, create_access_token, decode_access_token
from app.db.models.user import UserRole
from app.core.deps import get_current_user
from datetime import timedelta

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/login", response_model=LoginResponse)
async def login_user(login_in: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud_users.get_user_by_email(db, login_in.email)
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь заблокирован")
    access_token = create_access_token(subject=user.id)
    return LoginResponse(token=access_token, user={"id": user.id, "email": user.email, "role": user.role})

@router.get("/me", response_model=UserOut)
async def get_me_user(user=Depends(get_current_user)):
    return user

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(refresh_in: RefreshRequest):
    # TODO: Реализовать валидацию refresh_token и генерацию нового access token
    # Сейчас просто возвращает новый токен-заглушку
    return RefreshResponse(token="new-access-token", refresh_token=refresh_in.refresh_token)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    # TODO: Реализовать логику logout (например, blacklist refresh_token)
    return

