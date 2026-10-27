# api/v1/todo_api.py — refrigeradores y alimentos (requiere autenticación)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.v1.dependencies import get_current_active_user
from db.database import get_session
from models.Alimento_model import Alimento
from models.Refrigerador_model import Refrigerador
from models.user_model import Usuario
from schemas.Alimento import AlimentoCreate, AlimentoOut
from schemas.Refrigerador import RefrigeradorCreate, RefrigeradorOut

router_todo = APIRouter()


def _get_own_refrigerador(refrigerador_id: int, session: Session, user: Usuario) -> Refrigerador:
    refrigerador = session.get(Refrigerador, refrigerador_id)
    # 404 también cuando es de otro usuario, para no revelar que existe.
    if not refrigerador or refrigerador.usuario_id != user.id:
        raise HTTPException(status_code=404, detail="Refrigerador no encontrado")
    return refrigerador


@router_todo.post("/refrigeradores", response_model=RefrigeradorOut, status_code=status.HTTP_201_CREATED)
def crear_refrigerador(
    data: RefrigeradorCreate,
    session: Session = Depends(get_session),
    user: Usuario = Depends(get_current_active_user),
):
    refrigerador = Refrigerador(**data.model_dump(), usuario_id=user.id)
    session.add(refrigerador)
    session.commit()
    session.refresh(refrigerador)
    return refrigerador


@router_todo.get("/refrigeradores", response_model=list[RefrigeradorOut])
def listar_refrigeradores(
    session: Session = Depends(get_session),
    user: Usuario = Depends(get_current_active_user),
):
    return session.exec(select(Refrigerador).where(Refrigerador.usuario_id == user.id)).all()


@router_todo.get("/refrigeradores/{refrigerador_id}", response_model=RefrigeradorOut)
def obtener_refrigerador(
    refrigerador_id: int,
    session: Session = Depends(get_session),
    user: Usuario = Depends(get_current_active_user),
):
    return _get_own_refrigerador(refrigerador_id, session, user)


@router_todo.post(
    "/refrigeradores/{refrigerador_id}/alimentos",
    response_model=AlimentoOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_alimento(
    refrigerador_id: int,
    data: AlimentoCreate,
    session: Session = Depends(get_session),
    user: Usuario = Depends(get_current_active_user),
):
    _get_own_refrigerador(refrigerador_id, session, user)
    alimento = Alimento(**data.model_dump(), refrigerador_id=refrigerador_id)
    session.add(alimento)
    session.commit()
    session.refresh(alimento)
    return alimento
