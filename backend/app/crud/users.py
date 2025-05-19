from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.user import User, UserRole
from app.schemas.user import UserCreate, UserCreateWithRole
from app.core.security import get_password_hash, verify_password
from sqlalchemy.exc import IntegrityError

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: str):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_in: UserCreate, role: UserRole = UserRole.operator):
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=role
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        return None
    return db_user

async def create_user_with_role(db: AsyncSession, user_in: UserCreateWithRole):
    return await create_user(db, user_in, role=user_in.role)

async def update_user(db: AsyncSession, user_id: str, user_in):
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        return None
    return user

async def change_password(db: AsyncSession, user_id: str, old_password: str, new_password: str):
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    if not verify_password(old_password, user.hashed_password):
        return False
    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    await db.refresh(user)
    return True

# TODO: Для восстановления пароля потребуется хранить токены восстановления в БД или временно в памяти/Redis
# Здесь только заглушки для генерации и сброса пароля
async def set_reset_token(db: AsyncSession, user_id: str, token: str):
    # TODO: Сохранить токен в БД (например, в отдельной таблице или поле)
    pass

async def reset_password(db: AsyncSession, token: str, new_password: str):
    # TODO: Найти пользователя по токену, проверить срок действия, сбросить пароль
    pass

async def create_operator(db: AsyncSession, user_in: UserCreate, admin_id: str):
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=UserRole.operator,
        admin_id=admin_id
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        return None
    return db_user

async def get_operators_by_admin(db: AsyncSession, admin_id: str):
    result = await db.execute(select(User).where(User.role == UserRole.operator, User.admin_id == admin_id))
    return result.scalars().all()

async def update_operator(db: AsyncSession, operator_id: str, user_in):
    user = await get_user_by_id(db, operator_id)
    if not user or user.role != UserRole.operator:
        return None
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        return None
    return user

async def delete_operator(db: AsyncSession, operator_id: str):
    user = await get_user_by_id(db, operator_id)
    if not user or user.role != UserRole.operator:
        return False
    await db.delete(user)
    await db.commit()
    return True

