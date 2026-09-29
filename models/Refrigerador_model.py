# models.py
from typing import Optional, List
from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from models.user_model import Usuario  # Importamos el modelo de usuario para la relación   

# ============================================
# 2. MODELO REFRIGERADOR
# ============================================
class Refrigerador(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)  # ej: "Principal", "Del Garage"
    ubicacion: str
    
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship(back_populates="refrigeradores")
    
    # Un refrigerador tiene muchos alimentos (1:N DIRECTO)
    # cascade="all, delete-orphan" asegura que si borro el refri, se borran sus alimentos
    alimentos: List["Alimento"] = Relationship(
        back_populates="refrigerador",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )