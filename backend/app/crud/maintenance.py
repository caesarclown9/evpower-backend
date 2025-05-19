from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.maintenance import Maintenance, MaintenanceStatus
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.db.models.station import Station

async def get_maintenance_by_id(db: AsyncSession, maintenance_id: str) -> Optional[Maintenance]:
    result = await db.execute(select(Maintenance).where(Maintenance.id == maintenance_id))
    return result.scalar_one_or_none()

async def get_maintenances(db: AsyncSession, status: Optional[str] = None, station_id: Optional[str] = None) -> List[Maintenance]:
    query = select(Maintenance)
    if status:
        query = query.where(Maintenance.status == status)
    if station_id:
        query = query.where(Maintenance.station_id == station_id)
    result = await db.execute(query)
    return result.scalars().all()

async def get_maintenances_by_admin_id(db: AsyncSession, admin_id: str, status: Optional[str] = None) -> List[Maintenance]:
    # Получаем id всех станций admin
    stations_result = await db.execute(select(Station.id).where(Station.admin_id == admin_id))
    station_ids = [row[0] for row in stations_result.all()]
    if not station_ids:
        return []
    query = select(Maintenance).where(Maintenance.station_id.in_(station_ids))
    if status:
        query = query.where(Maintenance.status == status)
    result = await db.execute(query)
    return result.scalars().all()

async def create_maintenance(db: AsyncSession, maintenance_in: MaintenanceCreate) -> Optional[Maintenance]:
    db_maintenance = Maintenance(**maintenance_in.model_dump())
    db.add(db_maintenance)
    try:
        await db.commit()
        await db.refresh(db_maintenance)
    except IntegrityError:
        await db.rollback()
        return None
    return db_maintenance

async def update_maintenance(db: AsyncSession, maintenance_id: str, maintenance_in: MaintenanceUpdate) -> Optional[Maintenance]:
    maintenance = await get_maintenance_by_id(db, maintenance_id)
    if not maintenance:
        return None
    for field, value in maintenance_in.model_dump(exclude_unset=True).items():
        setattr(maintenance, field, value)
    try:
        await db.commit()
        await db.refresh(maintenance)
    except IntegrityError:
        await db.rollback()
        return None
    return maintenance

async def delete_maintenance(db: AsyncSession, maintenance_id: str) -> bool:
    maintenance = await get_maintenance_by_id(db, maintenance_id)
    if not maintenance:
        return False
    await db.delete(maintenance)
    await db.commit()
    return True
