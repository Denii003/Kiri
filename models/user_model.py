# models/user_model.py
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.Refrigerador_model import Refrigerador


def utcnow() -> datetime:
    """Fecha/hora actual en UTC, con zona horaria."""
    return datetime.now(timezone.utc)


class Usuario(SQLModel, table=True):
    """Modelo de Usuario (tabla 'usuario')."""

    __tablename__ = "usuario"

    # La PK es Optional porque la base de datos la genera al insertar.
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    email: str = Field(index=True, unique=True)
    # Nunca se guarda la contraseña: solo su hash Argon2.
    hashed_password: str
    is_active: bool = Field(default=True)
    # Nombre del objeto en MinIO (ej. "avatars/3/ab12.png"). None = sin foto.
    avatar_object: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))

    refrigeradores: List["Refrigerador"] = Relationship(back_populates="usuario")
