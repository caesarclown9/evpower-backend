from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.station import StationCreate, StationUpdate, Station, StationStatusUpdate
from app.crud import stations as crud_stations
from typing import List, Optional
from app.core.deps import get_current_user, require_role
from app.db.models.user import UserRole

router = APIRouter(prefix="/stations", tags=["stations"])

@router.get("/", response_model=List[Station])
async def list_stations(
    status: Optional[str] = Query(None),
    location_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    admin_id = None
    if user.role in [UserRole.admin, UserRole.operator]:
        admin_id = user.admin_id if user.role == UserRole.operator else user.id
    return await crud_stations.get_stations(db, status=status, location_id=location_id, admin_id=admin_id)

@router.post("/", response_model=Station, status_code=status.HTTP_201_CREATED)
async def create_station(station_in: StationCreate, db: AsyncSession = Depends(get_db), user=Depends(require_role('admin', 'operator', 'superadmin'))):
    # admin_id подставляется автоматически для admin/operator
    if user.role == UserRole.admin:
        station_in.admin_id = user.id
    elif user.role == UserRole.operator:
        station_in.admin_id = user.admin_id
    station = await crud_stations.create_station(db, station_in)
    if not station:
        raise HTTPException(status_code=400, detail="Ошибка создания станции")
    return station

@router.get("/{station_id}", response_model=Station)
async def get_station(station_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    station = await crud_stations.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    # Проверка доступа
    if user.role == UserRole.admin and station.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    if user.role == UserRole.operator and station.admin_id != user.admin_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    return station

@router.put("/{station_id}", response_model=Station)
async def update_station(station_id: str, station_in: StationUpdate, db: AsyncSession = Depends(get_db), user=Depends(require_role('admin', 'operator', 'superadmin'))):
    station = await crud_stations.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена или ошибка обновления")
    # Проверка доступа
    if user.role == UserRole.admin and station.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    if user.role == UserRole.operator and station.admin_id != user.admin_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    updated = await crud_stations.update_station(db, station_id, station_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Станция не найдена или ошибка обновления")
    return updated

@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_station(station_id: str, db: AsyncSession = Depends(get_db), user=Depends(require_role('admin', 'operator', 'superadmin'))):
    station = await crud_stations.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    # Проверка доступа
    if user.role == UserRole.admin and station.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    if user.role == UserRole.operator and station.admin_id != user.admin_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    success = await crud_stations.delete_station(db, station_id)
    if not success:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    return

@router.put("/{station_id}/status", response_model=Station)
async def update_station_status(station_id: str, status_in: StationStatusUpdate, db: AsyncSession = Depends(get_db), user=Depends(require_role('admin', 'operator', 'superadmin'))):
    station = await crud_stations.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена или ошибка обновления статуса")
    # Проверка доступа
    if user.role == UserRole.admin and station.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    if user.role == UserRole.operator and station.admin_id != user.admin_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    updated = await crud_stations.update_station_status(db, station_id, status_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Станция не найдена или ошибка обновления статуса")
    return updated
