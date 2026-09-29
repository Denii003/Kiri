# main.py
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlmodel import Session, select
from db.database import get_session
from models.Alimento_model import Refrigerador, Alimento
from schemas.Alimento import *


router_todo = APIRouter()



@router_todo.get("/refrigeradores/{refrigerador_id}", response_model=RefrigeradorOut)
def obtener_refrigerador(refrigerador_id: int, session: Session = Depends(get_session)):
    # SQLAlchemy hace el trabajo sucio. Al acceder a .alimentos, 
    # obtiene directamente los registros que tienen este refrigerador_id.
    refrigerador = session.get(Refrigerador, refrigerador_id)
    
    if not refrigerador:
        raise HTTPException(status_code=404, detail="Refrigerador no encontrado")
    
    return refrigerador # ¡Listo! Pydantic lo convierte a JSON con sus alimentos anidados.

@router_todo.post("/refrigeradores/{refrigerador_id}/alimentos", response_model=AlimentoOut)
def agregar_alimento(
    refrigerador_id: int, 
    alimento: Alimento, # Recibe nombre, tipo, cantidad, fecha_caducidad
    session: Session = Depends(get_session)
):
    refrigerador = session.get(Refrigerador, refrigerador_id)
    if not refrigerador:
        raise HTTPException(status_code=404, detail="Refrigerador no encontrado")
    
    # Asignamos la relación directamente
    alimento.refrigerador_id = refrigerador_id
    alimento.refrigerador = refrigerador
    
    session.add(alimento)
    session.commit()
    session.refresh(alimento)
    
    return alimento