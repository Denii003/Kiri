# schemas/Alimento.py
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AlimentoCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    tipo: str = Field(..., min_length=1)
    cantidad: int = Field(..., ge=0)
    fecha_caducidad: date


class AlimentoOut(BaseModel):
    id: int
    nombre: str
    tipo: str
    cantidad: int
    fecha_caducidad: date

    model_config = ConfigDict(from_attributes=True)
