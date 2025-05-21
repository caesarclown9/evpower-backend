from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.location import Location, LocationStatus
from app.schemas.location import LocationCreate, LocationUpdate
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

def get_location_by_id(db: Session, location_id: str) -> Optional[Location]:
    result = db.execute(select(Location).where(Location.id == location_id))
    return result.scalar_one_or_none()

def get_locations(db: Session, status: Optional[str] = None) -> List[Location]:
    query = select(Location)
    if status:
        query = query.where(Location.status == status)
    result = db.execute(query)
    return result.scalars().all()

def create_location(db: Session, location_in: LocationCreate) -> Optional[Location]:
    db_location = Location(**location_in.model_dump())
    db.add(db_location)
    try:
        db.commit()
        db.refresh(db_location)
    except IntegrityError:
        db.rollback()
        return None
    return db_location

def update_location(db: Session, location_id: str, location_in: LocationUpdate) -> Optional[Location]:
    location = get_location_by_id(db, location_id)
    if not location:
        return None
    for field, value in location_in.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    try:
        db.commit()
        db.refresh(location)
    except IntegrityError:
        db.rollback()
        return None
    return location

def delete_location(db: Session, location_id: str) -> bool:
    location = get_location_by_id(db, location_id)
    if not location:
        return False
    db.delete(location)
    db.commit()
    return True
