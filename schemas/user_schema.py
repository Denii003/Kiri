# schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


#OJO MUCHAHCONES
#LOS "..." SE LLAMAN ELIPSIS Y SIGNIFICAN QUE EL CAMPO ES OBLIGATORIO. SI NO PONES LOS "..." EL CAMPO SERÁ OPCIONAL.

# === Esquemas para CREAR usuario ===
class UserCreate(BaseModel):
    """Datos necesarios para crear un usuario"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr = Field(..., description="Correo electrónico")
    password: str = Field(..., min_length=8, max_length=72, description="Contraseña (mínimo 8 caracteres)")



# === Esquemas para ACTUALIZAR usuario ===

"""
¿UserUpdate puede tener campos que no están en UserCreate?
Sí, absolutamente. 

La regla es:
UserCreate: Solo los campos necesarios para crear (los que el usuario DEBE proporcionar)
UserUpdate: Cualquier campo que pueda cambiar (aunque no se haya usado en Create)
Ambos: Deben existir en el modelo SQLModel (User)

"""
class UserUpdate(BaseModel):
    """Datos opcionales para actualizar un usuario"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    is_active: Optional[bool] = None

# === Esquema de RESPUESTA (lo que devuelve la API) ===
"""
Pydantic normalmente espera un diccionario ({"id": 1, "username": "mike"}). Pero la base de datos le entrega un objeto de Python (db_user.id, db_user.username).
Al poner from_attributes = True, le estás diciendo a Pydantic: "Oye, si te doy un objeto, lee sus atributos usando el punto (.) en lugar de buscar claves de diccionario ([])".
"""
class UserResponse(BaseModel):
    """Datos del usuario que se devuelven en la respuesta"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Permite convertir modelos SQLModel a Pydantic