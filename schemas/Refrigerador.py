
from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List, Optional
from schemas.Alimento import AlimentoOut

class RefrigeradorOut(BaseModel):
    id: int
    nombre: str
    ubicacion: str
    # FastAPI serializará automáticamente la lista de alimentos
    alimentos: List[AlimentoOut] = []
    
    model_config = ConfigDict(from_attributes=True)