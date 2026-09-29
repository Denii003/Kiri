# schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List, Optional



class AlimentoOut(BaseModel):
    id: int
    nombre: str
    tipo: str
    cantidad: int
    fecha_caducidad: date
    
    model_config = ConfigDict(from_attributes=True)
