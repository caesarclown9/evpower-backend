from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.client import ClientCreate, ClientLogin, ClientOut
from app.crud import clients as crud_clients
from app.core.security import verify_password, create_access_token, decode_access_token
from datetime import timedelta

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/register", response_model=ClientOut)
async def register_client(client_in: ClientCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud_clients.get_client_by_email(db, client_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Клиент с таким email уже существует")
    client = await crud_clients.create_client(db, client_in)
    if not client:
        raise HTTPException(status_code=400, detail="Ошибка создания клиента")
    return client

@router.post("/login")
async def login_client(login_in: ClientLogin, db: AsyncSession = Depends(get_db)):
    client = await crud_clients.get_client_by_email(db, login_in.email)
    if not client or not verify_password(login_in.password, client.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if client.status != "active":
        raise HTTPException(status_code=403, detail="Клиент неактивен или заблокирован")
    access_token = create_access_token(subject=client.id)
    return {"token": access_token, "client": {"id": client.id, "email": client.email, "name": client.name}}

@router.get("/me", response_model=ClientOut)
async def get_me_client(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация клиента")
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    client_id = payload["sub"]
    client = await crud_clients.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return client

