from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from api.v1.dependencies import get_current_user
from core.config import settings
from core.security import create_access_token, get_password_hash, verify_password
from db.database import get_session
from models.user_model import Usuario
from schemas.token_schema import Token
from schemas.user_schema import UserCreate, UserResponse, UserUpdate


router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    if session.exec(select(Usuario).where(Usuario.email == user_data.email)).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    if session.exec(select(Usuario).where(Usuario.username == user_data.username)).first():
        raise HTTPException(status_code=400, detail="El username ya está en uso")

    db_user = Usuario(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(Usuario).where(Usuario.username == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/", response_model=list[UserResponse])
def get_users(
    session: Session = Depends(get_session),
    _current_user: Usuario = Depends(get_current_user),
):
    return session.exec(select(Usuario)).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {user_id} no encontrado")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session),
):
    db_user = session.get(Usuario, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {user_id} no encontrado")

    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(db_user, field, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(Usuario, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {user_id} no encontrado")
    session.delete(db_user)
    session.commit()
