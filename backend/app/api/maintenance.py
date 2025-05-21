from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceRequest, MaintenanceStatus
from app.crud import maintenance as crud_maintenance
from typing import List, Optional
from app.core.deps import get_current_user
from app.db.models.user import UserRole
from app.db.models.station import Station
from sqlalchemy import select
from app.crud.maintenance import get_maintenances_by_admin_id

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

@router.get("/", response_model=List[MaintenanceRequest])
def list_maintenance(
    status: Optional[MaintenanceStatus] = Query(None),
    station_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role == UserRole.admin:
        return get_maintenances_by_admin_id(db, user.id, status=status)
    elif user.role == UserRole.operator:
        return get_maintenances_by_admin_id(db, user.admin_id, status=status)
    else:
        return crud_maintenance.get_maintenances(db, status=status, station_id=station_id)

@router.post("/", response_model=MaintenanceRequest)
def create_maintenance(
    maintenance_in: MaintenanceCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud_maintenance.create_maintenance(db, maintenance_in)

@router.get("/{maintenance_id}", response_model=MaintenanceRequest)
def get_maintenance(
    maintenance_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    maintenance = crud_maintenance.get_maintenance_by_id(db, maintenance_id)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance not found")
    return maintenance

@router.put("/{maintenance_id}", response_model=MaintenanceRequest)
def update_maintenance(
    maintenance_id: str,
    maintenance_in: MaintenanceUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    maintenance = crud_maintenance.update_maintenance(db, maintenance_id, maintenance_in)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance not found")
    return maintenance

@router.delete("/{maintenance_id}")
def delete_maintenance(
    maintenance_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    result = crud_maintenance.delete_maintenance(db, maintenance_id)
    if not result:
        raise HTTPException(status_code=404, detail="Maintenance not found")
    return {"status": "deleted"}
