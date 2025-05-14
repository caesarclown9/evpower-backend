from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.station import StationCreate, StationUpdate, Station, StationStatusUpdate
from app.crud import stations as crud_stations
from typing import List, Optional

router = APIRouter(prefix="/stations", tags=["stations"])

@router.get("/", response_model=List[Station])
async def list_stations(
    status: Optional[str] = Query(None),
    location_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await crud_stations.get_stations(db, status=status, location_id=location_id)

@router.post("/", response_model=Station, status_code=status.HTTP_201_CREATED)
async def create_station(station_in: StationCreate, db: AsyncSession = Depends(get_db)):
    station = await crud_stations.create_station(db, station_in)
    if not station:
        raise HTTPException(status_code=400, detail="Ошибка создания станции")
    return station

@router.get("/{station_id}", response_model=Station)
async def get_station(station_id: str, db: AsyncSession = Depends(get_db)):
    station = await crud_stations.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    return station

@router.put("/{station_id}", response_model=Station)
async def update_station(station_id: str, station_in: StationUpdate, db: AsyncSession = Depends(get_db)):
    station = await crud_stations.update_station(db, station_id, station_in)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена или ошибка обновления")
    return station

@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_station(station_id: str, db: AsyncSession = Depends(get_db)):
    success = await crud_stations.delete_station(db, station_id)
    if not success:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    return

@router.put("/{station_id}/status", response_model=Station)
async def update_station_status(station_id: str, status_in: StationStatusUpdate, db: AsyncSession = Depends(get_db)):
    station = await crud_stations.update_station_status(db, station_id, status_in)
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена или ошибка обновления статуса")
    return station
