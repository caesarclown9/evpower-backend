from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
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
async def list_maintenance(
    status: Optional[MaintenanceStatus] = Query(None),
    station_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role == UserRole.admin:
        return await get_maintenances_by_admin_id(db, user.id, status=status)
    elif user.role == UserRole.operator:
        return await get_maintenances_by_admin_id(db, user.admin_id, status=status)
    else:
        return await crud_maintenance.get_maintenances(db, status=status, station_id=station_id)

@router.post("/", response_model=MaintenanceRequest, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    maintenance_in: MaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    # Проверка, что пользователь может создавать заявку только на свою станцию
    station = await db.execute(select(Station).where(Station.id == maintenance_in.station_id))
    station = station.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    if user.role == UserRole.admin and station.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    if user.role == UserRole.operator and station.admin_id != user.admin_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой станции")
    maintenance = await crud_maintenance.create_maintenance(db, maintenance_in)
    if not maintenance:
        raise HTTPException(status_code=400, detail="Ошибка создания заявки на обслуживание")
    return maintenance

@router.get("/{maintenance_id}", response_model=MaintenanceRequest)
async def get_maintenance(
    maintenance_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    maintenance = await crud_maintenance.get_maintenance_by_id(db, maintenance_id)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Заявка на обслуживание не найдена")
    # Проверка доступа
    station = await db.execute(select(Station).where(Station.id == maintenance.station_id))
    station = station.scalar_one_or_none()
    if user.role == UserRole.admin and station and station.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой заявке")
    if user.role == UserRole.operator and station and station.admin_id != user.admin_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой заявке")
    return maintenance

@router.put("/{maintenance_id}", response_model=MaintenanceRequest)
async def update_maintenance(
    maintenance_id: str,
    maintenance_in: MaintenanceUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    maintenance = await crud_maintenance.get_maintenance_by_id(db, maintenance_id)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Заявка на обслуживание не найдена или ошибка обновления")
    # Проверка доступа
    station = await db.execute(select(Station).where(Station.id == maintenance.station_id))
    station = station.scalar_one_or_none()
    if user.role == UserRole.admin and station and station.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой заявке")
    if user.role == UserRole.operator and station and station.admin_id != user.admin_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой заявке")
    updated = await crud_maintenance.update_maintenance(db, maintenance_id, maintenance_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Заявка на обслуживание не найдена или ошибка обновления")
    return updated

@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance(
    maintenance_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    maintenance = await crud_maintenance.get_maintenance_by_id(db, maintenance_id)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Заявка на обслуживание не найдена")
    # Проверка доступа
    station = await db.execute(select(Station).where(Station.id == maintenance.station_id))
    station = station.scalar_one_or_none()
    if user.role == UserRole.admin and station and station.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой заявке")
    if user.role == UserRole.operator and station and station.admin_id != user.admin_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой заявке")
    success = await crud_maintenance.delete_maintenance(db, maintenance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Заявка на обслуживание не найдена")
    return
