from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.ocpp import (
    OCPPConnection, OCPPConnectionCreate,
    OCPPTransaction, OCPPTransactionCreate
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/ocpp", tags=["ocpp"])

@router.get("/connections", response_model=List[OCPPConnection])
async def list_ocpp_connections(user=Depends(get_current_user)):
    # TODO: Реализовать бизнес-логику получения списка соединений
    return []

@router.post("/connections", response_model=OCPPConnection, status_code=status.HTTP_201_CREATED)
async def create_ocpp_connection(
    connection_in: OCPPConnectionCreate,
    user=Depends(get_current_user)
):
    # TODO: Реализовать бизнес-логику создания соединения
    return OCPPConnection(id="ocpp-conn-001", station_id=connection_in.station_id, status="active", last_heartbeat=None)

@router.get("/transactions", response_model=List[OCPPTransaction])
async def list_ocpp_transactions(user=Depends(get_current_user)):
    # TODO: Реализовать бизнес-логику получения списка транзакций
    return []

@router.post("/transactions", response_model=OCPPTransaction, status_code=status.HTTP_201_CREATED)
async def create_ocpp_transaction(
    transaction_in: OCPPTransactionCreate,
    user=Depends(get_current_user)
):
    # TODO: Реализовать бизнес-логику создания транзакции
    return OCPPTransaction(id="ocpp-trx-001", connection_id=transaction_in.connection_id, start_time=transaction_in.start_time, stop_time=None, energy=None, status="started")
