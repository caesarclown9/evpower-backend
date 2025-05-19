from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.db.models.ocpp import Tariff, ChargingSession
from app.schemas.ocpp import TariffCreate, ChargingSessionCreate

# --- Tariff CRUD ---
async def create_tariff(db: AsyncSession, tariff_in: TariffCreate) -> Tariff:
    tariff = Tariff(**tariff_in.model_dump())
    db.add(tariff)
    await db.commit()
    await db.refresh(tariff)
    return tariff

async def get_tariff(db: AsyncSession, tariff_id: str) -> Tariff | None:
    result = await db.execute(select(Tariff).where(Tariff.id == tariff_id))
    return result.scalar_one_or_none()

async def list_tariffs(db: AsyncSession, station_id: str | None = None) -> list[Tariff]:
    stmt = select(Tariff)
    if station_id:
        stmt = stmt.where(Tariff.station_id == station_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_tariff(db: AsyncSession, tariff_id: str, data: dict) -> Tariff | None:
    await db.execute(update(Tariff).where(Tariff.id == tariff_id).values(**data))
    await db.commit()
    return await get_tariff(db, tariff_id)

async def delete_tariff(db: AsyncSession, tariff_id: str) -> None:
    await db.execute(delete(Tariff).where(Tariff.id == tariff_id))
    await db.commit()

# --- ChargingSession CRUD ---
async def create_charging_session(db: AsyncSession, session_in: ChargingSessionCreate) -> ChargingSession:
    session = ChargingSession(**session_in.model_dump())
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def get_charging_session(db: AsyncSession, session_id: str) -> ChargingSession | None:
    result = await db.execute(select(ChargingSession).where(ChargingSession.id == session_id))
    return result.scalar_one_or_none()

async def list_charging_sessions(db: AsyncSession, user_id: str | None = None, station_id: str | None = None) -> list[ChargingSession]:
    stmt = select(ChargingSession)
    if user_id:
        stmt = stmt.where(ChargingSession.user_id == user_id)
    if station_id:
        stmt = stmt.where(ChargingSession.station_id == station_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_charging_session(db: AsyncSession, session_id: str, data: dict) -> ChargingSession | None:
    await db.execute(update(ChargingSession).where(ChargingSession.id == session_id).values(**data))
    await db.commit()
    return await get_charging_session(db, session_id)

async def delete_charging_session(db: AsyncSession, session_id: str) -> None:
    await db.execute(delete(ChargingSession).where(ChargingSession.id == session_id))
    await db.commit()

