from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.station import Station, StationStatus
from app.schemas.station import StationCreate, StationUpdate, StationStatusUpdate
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

def get_station_by_id(db: Session, station_id: str) -> Optional[Station]:
    result = db.execute(select(Station).where(Station.id == station_id))
    return result.scalar_one_or_none()

def get_stations(db: Session, status: Optional[str] = None, location_id: Optional[str] = None, admin_id: Optional[str] = None) -> List[Station]:
    query = select(Station)
    if status:
        query = query.where(Station.status == status)
    if location_id:
        query = query.where(Station.location_id == location_id)
    if admin_id:
        query = query.where(Station.admin_id == admin_id)
    result = db.execute(query)
    return result.scalars().all()

def create_station(db: Session, station_in: StationCreate) -> Optional[Station]:
    db_station = Station(**station_in.model_dump())
    db.add(db_station)
    try:
        db.commit()
        db.refresh(db_station)
    except IntegrityError:
        db.rollback()
        return None
    return db_station

def update_station(db: Session, station_id: str, station_in: StationUpdate) -> Optional[Station]:
    station = get_station_by_id(db, station_id)
    if not station:
        return None
    for field, value in station_in.model_dump(exclude_unset=True).items():
        setattr(station, field, value)
    try:
        db.commit()
        db.refresh(station)
    except IntegrityError:
        db.rollback()
        return None
    return station

def delete_station(db: Session, station_id: str) -> bool:
    station = get_station_by_id(db, station_id)
    if not station:
        return False
    db.delete(station)
    db.commit()
    return True

def update_station_status(db: Session, station_id: str, status_in: StationStatusUpdate) -> Optional[Station]:
    station = get_station_by_id(db, station_id)
    if not station:
        return None
    station.status = status_in.status
    db.commit()
    db.refresh(station)
    return station
