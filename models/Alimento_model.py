# models/Alimento_model.py
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.Refrigerador_model import Refrigerador


class Alimento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)  # ej: "Leche Alpura"
    tipo: str = Field(index=True)    # ej: "Lácteo"
    cantidad: int = Field(ge=0)
    fecha_caducidad: date = Field(index=True)

    refrigerador_id: Optional[int] = Field(default=None, foreign_key="refrigerador.id")
    refrigerador: Optional["Refrigerador"] = Relationship(back_populates="alimentos")
