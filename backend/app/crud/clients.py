from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.client import Client, ClientStatus
from app.schemas.client import ClientCreate
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError

async def get_client_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(Client).where(Client.email == email))
    return result.scalar_one_or_none()

async def get_client_by_id(db: AsyncSession, client_id: str):
    result = await db.execute(select(Client).where(Client.id == client_id))
    return result.scalar_one_or_none()

async def create_client(db: AsyncSession, client_in: ClientCreate):
    hashed_password = get_password_hash(client_in.password)
    db_client = Client(
        name=client_in.name,
        email=client_in.email,
        phone=client_in.phone,
        address=client_in.address,
        contract_number=client_in.contract_number,
        status=client_in.status or ClientStatus.active,
        hashed_password=hashed_password
    )
    db.add(db_client)
    try:
        await db.commit()
        await db.refresh(db_client)
    except IntegrityError:
        await db.rollback()
        return None
    return db_client

async def update_client(db: AsyncSession, client_id: str, client_in):
    client = await get_client_by_id(db, client_id)
    if not client:
        return None
    for field, value in client_in.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    try:
        await db.commit()
        await db.refresh(client)
    except IntegrityError:
        await db.rollback()
        return None
    return client

async def change_client_password(db: AsyncSession, client_id: str, old_password: str, new_password: str):
    client = await get_client_by_id(db, client_id)
    if not client:
        return None
    from app.core.security import verify_password, get_password_hash
    if not verify_password(old_password, client.hashed_password):
        return False
    client.hashed_password = get_password_hash(new_password)
    await db.commit()
    await db.refresh(client)
    return True

# TODO: Для восстановления пароля потребуется хранить токены восстановления в БД или временно в памяти/Redis
# Здесь только заглушки для генерации и сброса пароля
async def set_client_reset_token(db: AsyncSession, client_id: str, token: str):
    # TODO: Сохранить токен в БД (например, в отдельной таблице или поле)
    pass

async def reset_client_password(db: AsyncSession, token: str, new_password: str):
    # TODO: Найти клиента по токену, проверить срок действия, сбросить пароль
    pass
