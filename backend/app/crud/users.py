from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.user import User, UserRole
from app.schemas.user import UserCreate, UserCreateWithRole
from app.core.security import get_password_hash, verify_password
from sqlalchemy.exc import IntegrityError

def get_user_by_email(db: Session, email: str):
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

def get_user_by_id(db: Session, user_id: str):
    result = db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

def create_user(db: Session, user_in: UserCreate, role: UserRole = UserRole.operator):
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=role
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        return None
    return db_user

def create_user_with_role(db: Session, user_in: UserCreateWithRole):
    return create_user(db, user_in, role=user_in.role)

def update_user(db: Session, user_id: str, user_in):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        return None
    return user

def change_password(db: Session, user_id: str, old_password: str, new_password: str):
    user = get_user_by_id(db, user_id)
    if not user or not verify_password(old_password, user.hashed_password):
        return None
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user

def set_reset_token(db: Session, user_id: str, token: str):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.reset_token = token
    db.commit()
    db.refresh(user)
    return user

def reset_password(db: Session, token: str, new_password: str):
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        return None
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    db.commit()
    db.refresh(user)
    return user

def create_operator(db: Session, user_in: UserCreate, admin_id: str):
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=UserRole.operator,
        admin_id=admin_id
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        return None
    return db_user

def get_operators_by_admin(db: Session, admin_id: str):
    result = db.execute(select(User).where(User.role == UserRole.operator, User.admin_id == admin_id))
    return result.scalars().all()

def update_operator(db: Session, operator_id: str, user_in):
    user = get_user_by_id(db, operator_id)
    if not user:
        return None
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        return None
    return user

def delete_operator(db: Session, operator_id: str):
    user = get_user_by_id(db, operator_id)
    if not user:
        return None
    db.delete(user)
    db.commit()
    return True

