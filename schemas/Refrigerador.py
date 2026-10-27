# schemas/Refrigerador.py
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from schemas.Alimento import AlimentoOut


class RefrigeradorCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    ubicacion: str = Field(..., min_length=1)


class RefrigeradorOut(BaseModel):
    id: int
    nombre: str
    ubicacion: str
    alimentos: List[AlimentoOut] = []

    model_config = ConfigDict(from_attributes=True)
