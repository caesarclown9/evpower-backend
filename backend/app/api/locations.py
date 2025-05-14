from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.location import LocationCreate, LocationUpdate, Location
from app.crud import locations as crud_locations
from typing import List, Optional

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/", response_model=List[Location])
async def list_locations(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await crud_locations.get_locations(db, status=status)

@router.post("/", response_model=Location, status_code=status.HTTP_201_CREATED)
async def create_location(location_in: LocationCreate, db: AsyncSession = Depends(get_db)):
    location = await crud_locations.create_location(db, location_in)
    if not location:
        raise HTTPException(status_code=400, detail="Ошибка создания локации")
    return location

@router.get("/{location_id}", response_model=Location)
async def get_location(location_id: str, db: AsyncSession = Depends(get_db)):
    location = await crud_locations.get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Локация не найдена")
    return location

@router.put("/{location_id}", response_model=Location)
async def update_location(location_id: str, location_in: LocationUpdate, db: AsyncSession = Depends(get_db)):
    location = await crud_locations.update_location(db, location_id, location_in)
    if not location:
        raise HTTPException(status_code=404, detail="Локация не найдена или ошибка обновления")
    return location

@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(location_id: str, db: AsyncSession = Depends(get_db)):
    success = await crud_locations.delete_location(db, location_id)
    if not success:
        raise HTTPException(status_code=404, detail="Локация не найдена")
    return
