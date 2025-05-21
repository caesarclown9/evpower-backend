from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.client import Client, ClientStatus
from app.schemas.client import ClientCreate
from app.core.security import get_password_hash, verify_password
from sqlalchemy.exc import IntegrityError

def get_client_by_email(db: Session, email: str):
    result = db.execute(select(Client).where(Client.email == email))
    return result.scalar_one_or_none()

def get_client_by_id(db: Session, client_id: str):
    result = db.execute(select(Client).where(Client.id == client_id))
    return result.scalar_one_or_none()

def create_client(db: Session, client_in: ClientCreate):
    hashed_password = get_password_hash(client_in.password)
    db_client = Client(
        email=client_in.email,
        hashed_password=hashed_password,
        status=ClientStatus.active
    )
    db.add(db_client)
    try:
        db.commit()
        db.refresh(db_client)
    except IntegrityError:
        db.rollback()
        return None
    return db_client

def update_client(db: Session, client_id: str, client_in):
    client = get_client_by_id(db, client_id)
    if not client:
        return None
    for field, value in client_in.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    try:
        db.commit()
        db.refresh(client)
    except IntegrityError:
        db.rollback()
        return None
    return client

def change_client_password(db: Session, client_id: str, old_password: str, new_password: str):
    client = get_client_by_id(db, client_id)
    if not client or not verify_password(old_password, client.hashed_password):
        return None
    client.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(client)
    return client

def set_client_reset_token(db: Session, client_id: str, token: str):
    client = get_client_by_id(db, client_id)
    if not client:
        return None
    client.reset_token = token
    db.commit()
    db.refresh(client)
    return client

def reset_client_password(db: Session, token: str, new_password: str):
    client = db.query(Client).filter(Client.reset_token == token).first()
    if not client:
        return None
    client.hashed_password = get_password_hash(new_password)
    client.reset_token = None
    db.commit()
    db.refresh(client)
    return client
