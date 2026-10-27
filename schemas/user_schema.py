# schemas/user_schema.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Datos necesarios para registrar un usuario (el campo '...' = obligatorio)."""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr = Field(..., description="Correo electrónico")
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña (mínimo 8 caracteres)")


class UserUpdate(BaseModel):
    """Campos opcionales para actualizar un usuario."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Lo que devuelve la API: nunca incluye la contraseña ni su hash."""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    avatar_url: Optional[str] = None  # URL firmada temporal de MinIO

    model_config = ConfigDict(from_attributes=True)
