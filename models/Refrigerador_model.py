# models/Refrigerador_model.py
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.Alimento_model import Alimento
    from models.user_model import Usuario


class Refrigerador(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)  # ej: "Principal", "Del Garage"
    ubicacion: str

    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario: Optional["Usuario"] = Relationship(back_populates="refrigeradores")

    # 1:N — si se borra el refrigerador, se borran sus alimentos.
    alimentos: List["Alimento"] = Relationship(
        back_populates="refrigerador",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
