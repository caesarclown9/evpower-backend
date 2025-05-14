from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceRequest, MaintenanceStatus
from app.crud import maintenance as crud_maintenance
from typing import List, Optional
from app.core.deps import get_current_user

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

@router.get("/", response_model=List[MaintenanceRequest])
async def list_maintenance(
    status: Optional[MaintenanceStatus] = Query(None),
    station_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await crud_maintenance.get_maintenances(db, status=status, station_id=station_id)

@router.post("/", response_model=MaintenanceRequest, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    maintenance_in: MaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
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
    return maintenance

@router.put("/{maintenance_id}", response_model=MaintenanceRequest)
async def update_maintenance(
    maintenance_id: str,
    maintenance_in: MaintenanceUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    maintenance = await crud_maintenance.update_maintenance(db, maintenance_id, maintenance_in)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Заявка на обслуживание не найдена или ошибка обновления")
    return maintenance

@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance(
    maintenance_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    success = await crud_maintenance.delete_maintenance(db, maintenance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Заявка на обслуживание не найдена")
    return
