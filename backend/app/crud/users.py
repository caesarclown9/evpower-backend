from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.user import User, UserRole
from app.schemas.user import UserCreate, UserCreateWithRole
from app.core.security import get_password_hash
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

