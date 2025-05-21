from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.station import StationCreate, StationUpdate, Station, StationStatusUpdate
from app.crud import stations as crud_stations
from typing import List, Optional
from app.core.deps import get_current_user, require_role
from app.db.models.user import UserRole

router = APIRouter(prefix="/stations", tags=["stations"])

@router.get("/", response_model=List[Station])
def list_stations(
    status: Optional[str] = Query(None),
    location_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    admin_id = None
    if user.role in [UserRole.admin, UserRole.operator]:
        admin_id = user.admin_id if user.role == UserRole.operator else user.id
    return crud_stations.get_stations(db, status=status, location_id=location_id, admin_id=admin_id)

@router.post("/", response_model=Station)
def create_station(station_in: StationCreate, db: Session = Depends(get_db), user=Depends(require_role('admin', 'operator', 'superadmin'))):
    return crud_stations.create_station(db, station_in)

@router.get("/{station_id}", response_model=Station)
def get_station(station_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    station = crud_stations.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    return station

@router.put("/{station_id}", response_model=Station)
def update_station(station_id: str, station_in: StationUpdate, db: Session = Depends(get_db), user=Depends(require_role('admin', 'operator', 'superadmin'))):
    station = crud_stations.update_station(db, station_id, station_in)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    return station

@router.delete("/{station_id}")
def delete_station(station_id: str, db: Session = Depends(get_db), user=Depends(require_role('admin', 'operator', 'superadmin'))):
    result = crud_stations.delete_station(db, station_id)
    if not result:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    return {"status": "deleted"}

@router.patch("/{station_id}/status", response_model=Station)
def update_station_status(station_id: str, status_in: StationStatusUpdate, db: Session = Depends(get_db), user=Depends(require_role('admin', 'operator', 'superadmin'))):
    station = crud_stations.update_station_status(db, station_id, status_in)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    return station
