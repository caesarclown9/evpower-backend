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
