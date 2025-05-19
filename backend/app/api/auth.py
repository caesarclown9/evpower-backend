from fastapi import APIRouter, Depends, HTTPException, status, Request, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserOut, ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest, UserUpdate, UserCreateWithRole, UserCreate
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, RefreshResponse
from app.crud import users as crud_users
from app.core.security import verify_password, create_access_token, decode_access_token
from app.db.models.user import UserRole
from app.core.deps import get_current_user, require_role
from datetime import timedelta
from app.crud.users import create_user_with_role, create_operator, get_operators_by_admin, update_operator, delete_operator
from sqlalchemy import select

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

@router.post("/change-password", status_code=200)
async def change_password(
    req: ChangePasswordRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await crud_users.change_password(db, user.id, req.old_password, req.new_password)
    if result is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if result is False:
        raise HTTPException(status_code=400, detail="Старый пароль неверен")
    return {"detail": "Пароль успешно изменён"}

@router.post("/forgot-password", status_code=200)
async def forgot_password(
    req: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    # TODO: Реализовать генерацию токена и отправку email
    user = await crud_users.get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    # Здесь должна быть генерация токена и отправка письма
    # await crud_users.set_reset_token(db, user.id, token)
    return {"detail": "Инструкция по восстановлению пароля отправлена на email (заглушка)"}

@router.post("/reset-password", status_code=200)
async def reset_password(
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    # TODO: Реализовать сброс пароля по токену
    # result = await crud_users.reset_password(db, req.token, req.new_password)
    # if not result:
    #     raise HTTPException(status_code=400, detail="Неверный или истёкший токен")
    return {"detail": "Пароль успешно сброшен (заглушка)"}

@router.put("/me", response_model=UserOut)
async def update_profile(
    update_in: UserUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated = await crud_users.update_user(db, user.id, update_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Пользователь не найден или ошибка обновления")
    return updated

@router.post("/register", response_model=UserOut, summary="Регистрация пользователя (только для superadmin)")
async def register_user(
    user_in: UserCreateWithRole,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role('superadmin'))
):
    db_user = await create_user_with_role(db, user_in)
    if not db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    return db_user

# --- Управление операторами ---
@router.post("/operators", response_model=UserOut, summary="Создать оператора (только для admin)")
async def create_operator_endpoint(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role('admin', 'superadmin'))
):
    # Только admin может создавать операторов для себя
    admin_id = current_user.id if current_user.role == UserRole.admin else user_in.admin_id
    if current_user.role == UserRole.admin:
        user = await create_operator(db, user_in, admin_id=admin_id)
    else:
        # superadmin может указать admin_id явно
        if not user_in.admin_id:
            raise HTTPException(status_code=400, detail="admin_id обязателен для оператора")
        user = await create_operator(db, user_in, admin_id=user_in.admin_id)
    if not user:
        raise HTTPException(status_code=400, detail="Ошибка создания оператора")
    return user

@router.get("/operators", response_model=list[UserOut], summary="Список своих операторов (только для admin)")
async def list_operators_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role('admin', 'superadmin'))
):
    admin_id = current_user.id if current_user.role == UserRole.admin else None
    if current_user.role == UserRole.admin:
        return await get_operators_by_admin(db, admin_id=admin_id)
    else:
        # superadmin видит всех операторов
        result = await db.execute(select(User).where(User.role == UserRole.operator))
        return result.scalars().all()

@router.put("/operators/{operator_id}", response_model=UserOut, summary="Редактировать оператора (только для admin)")
async def update_operator_endpoint(
    operator_id: str = Path(...),
    user_in: UserUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role('admin', 'superadmin'))
):
    # Проверка, что оператор принадлежит этому admin
    operator = await crud_users.get_user_by_id(db, operator_id)
    if not operator or operator.role != UserRole.operator:
        raise HTTPException(status_code=404, detail="Оператор не найден")
    if current_user.role == UserRole.admin and operator.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому оператору")
    updated = await update_operator(db, operator_id, user_in)
    if not updated:
        raise HTTPException(status_code=400, detail="Ошибка обновления оператора")
    return updated

@router.delete("/operators/{operator_id}", status_code=204, summary="Удалить оператора (только для admin)")
async def delete_operator_endpoint(
    operator_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role('admin', 'superadmin'))
):
    operator = await crud_users.get_user_by_id(db, operator_id)
    if not operator or operator.role != UserRole.operator:
        raise HTTPException(status_code=404, detail="Оператор не найден")
    if current_user.role == UserRole.admin and operator.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому оператору")
    success = await delete_operator(db, operator_id)
    if not success:
        raise HTTPException(status_code=400, detail="Ошибка удаления оператора")
    return

