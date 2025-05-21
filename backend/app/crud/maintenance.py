from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.maintenance import Maintenance, MaintenanceStatus
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.db.models.station import Station

def get_maintenance_by_id(db: Session, maintenance_id: str) -> Optional[Maintenance]:
    result = db.execute(select(Maintenance).where(Maintenance.id == maintenance_id))
    return result.scalar_one_or_none()

def get_maintenances(db: Session, status: Optional[str] = None, station_id: Optional[str] = None) -> List[Maintenance]:
    query = select(Maintenance)
    if status:
        query = query.where(Maintenance.status == status)
    if station_id:
        query = query.where(Maintenance.station_id == station_id)
    result = db.execute(query)
    return result.scalars().all()

def get_maintenances_by_admin_id(db: Session, admin_id: str, status: Optional[str] = None) -> List[Maintenance]:
    stations_result = db.execute(select(Station.id).where(Station.admin_id == admin_id))
    station_ids = [row[0] for row in stations_result.all()]
    if not station_ids:
        return []
    query = select(Maintenance).where(Maintenance.station_id.in_(station_ids))
    if status:
        query = query.where(Maintenance.status == status)
    result = db.execute(query)
    return result.scalars().all()

def create_maintenance(db: Session, maintenance_in: MaintenanceCreate) -> Optional[Maintenance]:
    db_maintenance = Maintenance(**maintenance_in.model_dump())
    db.add(db_maintenance)
    try:
        db.commit()
        db.refresh(db_maintenance)
    except IntegrityError:
        db.rollback()
        return None
    return db_maintenance

def update_maintenance(db: Session, maintenance_id: str, maintenance_in: MaintenanceUpdate) -> Optional[Maintenance]:
    maintenance = get_maintenance_by_id(db, maintenance_id)
    if not maintenance:
        return None
    for field, value in maintenance_in.model_dump(exclude_unset=True).items():
        setattr(maintenance, field, value)
    try:
        db.commit()
        db.refresh(maintenance)
    except IntegrityError:
        db.rollback()
        return None
    return maintenance

def delete_maintenance(db: Session, maintenance_id: str) -> bool:
    maintenance = get_maintenance_by_id(db, maintenance_id)
    if not maintenance:
        return False
    db.delete(maintenance)
    db.commit()
    return True
