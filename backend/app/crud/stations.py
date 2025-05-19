from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.station import Station, StationStatus
from app.schemas.station import StationCreate, StationUpdate, StationStatusUpdate
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

async def get_station_by_id(db: AsyncSession, station_id: str) -> Optional[Station]:
    result = await db.execute(select(Station).where(Station.id == station_id))
    return result.scalar_one_or_none()

async def get_stations(db: AsyncSession, status: Optional[str] = None, location_id: Optional[str] = None, admin_id: Optional[str] = None) -> List[Station]:
    query = select(Station)
    if status:
        query = query.where(Station.status == status)
    if location_id:
        query = query.where(Station.location_id == location_id)
    if admin_id:
        query = query.where(Station.admin_id == admin_id)
    result = await db.execute(query)
    return result.scalars().all()

async def create_station(db: AsyncSession, station_in: StationCreate) -> Optional[Station]:
    db_station = Station(**station_in.model_dump())
    db.add(db_station)
    try:
        await db.commit()
        await db.refresh(db_station)
    except IntegrityError:
        await db.rollback()
        return None
    return db_station

async def update_station(db: AsyncSession, station_id: str, station_in: StationUpdate) -> Optional[Station]:
    station = await get_station_by_id(db, station_id)
    if not station:
        return None
    for field, value in station_in.model_dump(exclude_unset=True).items():
        setattr(station, field, value)
    try:
        await db.commit()
        await db.refresh(station)
    except IntegrityError:
        await db.rollback()
        return None
    return station

async def delete_station(db: AsyncSession, station_id: str) -> bool:
    station = await get_station_by_id(db, station_id)
    if not station:
        return False
    await db.delete(station)
    await db.commit()
    return True

async def update_station_status(db: AsyncSession, station_id: str, status_in: StationStatusUpdate) -> Optional[Station]:
    station = await get_station_by_id(db, station_id)
    if not station:
        return None
    station.status = status_in.status
    # Можно сохранить reason в отдельное поле или лог, если потребуется
    await db.commit()
    await db.refresh(station)
    return station
