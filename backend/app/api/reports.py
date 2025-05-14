from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.schemas.report import UsageReport, RevenueReport
from app.core.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/usage", response_model=List[UsageReport])
async def get_usage_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user=Depends(get_current_user)
):
    # TODO: Реализовать бизнес-логику получения usage-отчёта
    return []

@router.get("/revenue", response_model=List[RevenueReport])
async def get_revenue_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user=Depends(get_current_user)
):
    # TODO: Реализовать бизнес-логику получения revenue-отчёта
    return []
