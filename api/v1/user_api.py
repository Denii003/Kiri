# api/v1/user_api.py
from datetime import timedelta

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.v1.dependencies import get_current_active_user
from core import storage
from core.config import settings
from core.security import create_access_token, get_password_hash, verify_password
from db.database import get_session
from models.user_model import Usuario
from schemas.token_schema import Token
from schemas.user_schema import UserCreate, UserResponse, UserUpdate

router = APIRouter()


def to_response(user: Usuario) -> UserResponse:
    """Convierte el modelo en respuesta, generando la URL firmada de la foto si existe."""
    response = UserResponse.model_validate(user)
    if user.avatar_object:
        response.avatar_url = storage.get_presigned_url(user.avatar_object)
    return response


def _get_own_user(user_id: int, current_user: Usuario) -> Usuario:
    """Solo se puede operar sobre la propia cuenta."""
    if user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso sobre este usuario")
    return current_user


# ---------- Registro y login ----------
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
    return to_response(db_user)


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(Usuario).where(Usuario.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ---------- Perfil propio y foto (MinIO) — deben ir ANTES de "/{user_id}" ----------
@router.get("/me", response_model=UserResponse)
def read_me(current_user: Usuario = Depends(get_current_active_user)):
    return to_response(current_user)


@router.post("/me/avatar", response_model=UserResponse)
def upload_my_avatar(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user),
):
    new_object = storage.upload_avatar(current_user.id, file)
    old_object = current_user.avatar_object
    current_user.avatar_object = new_object
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    if old_object:
        storage.delete_object(old_object)
    return to_response(current_user)


@router.delete("/me/avatar", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_avatar(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user),
):
    if current_user.avatar_object:
        storage.delete_object(current_user.avatar_object)
        current_user.avatar_object = None
        session.add(current_user)
        session.commit()


# ---------- CRUD ----------
@router.get("/", response_model=list[UserResponse])
def get_users(
    session: Session = Depends(get_session),
    _current_user: Usuario = Depends(get_current_active_user),
):
    return [to_response(u) for u in session.exec(select(Usuario)).all()]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    _current_user: Usuario = Depends(get_current_active_user),
):
    user = session.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {user_id} no encontrado")
    return to_response(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user),
):
    db_user = _get_own_user(user_id, current_user)

    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(db_user, field, value)
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="El username o email ya está en uso")
    session.refresh(db_user)
    return to_response(db_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user),
):
    db_user = _get_own_user(user_id, current_user)
    if db_user.avatar_object:
        storage.delete_object(db_user.avatar_object)
    session.delete(db_user)
    session.commit()
