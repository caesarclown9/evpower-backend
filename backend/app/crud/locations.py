from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.location import Location, LocationStatus
from app.schemas.location import LocationCreate, LocationUpdate
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

async def get_location_by_id(db: AsyncSession, location_id: str) -> Optional[Location]:
    result = await db.execute(select(Location).where(Location.id == location_id))
    return result.scalar_one_or_none()

async def get_locations(db: AsyncSession, status: Optional[str] = None) -> List[Location]:
    query = select(Location)
    if status:
        query = query.where(Location.status == status)
    result = await db.execute(query)
    return result.scalars().all()

async def create_location(db: AsyncSession, location_in: LocationCreate) -> Optional[Location]:
    db_location = Location(**location_in.model_dump())
    db.add(db_location)
    try:
        await db.commit()
        await db.refresh(db_location)
    except IntegrityError:
        await db.rollback()
        return None
    return db_location

async def update_location(db: AsyncSession, location_id: str, location_in: LocationUpdate) -> Optional[Location]:
    location = await get_location_by_id(db, location_id)
    if not location:
        return None
    for field, value in location_in.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    try:
        await db.commit()
        await db.refresh(location)
    except IntegrityError:
        await db.rollback()
        return None
    return location

async def delete_location(db: AsyncSession, location_id: str) -> bool:
    location = await get_location_by_id(db, location_id)
    if not location:
        return False
    await db.delete(location)
    await db.commit()
    return True
