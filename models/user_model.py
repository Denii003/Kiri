# models/user_model.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


"""

A primera vista parece un error: ¿cómo va a ser opcional la llave primaria de una tabla?
Pero en realidad, es la forma correcta y estándar de hacerlo en SQLModel. Piensa en el "ciclo de vida" de un objeto antes y 
después de guardarlo en la base de datos.


Cuando creas un usuario nuevo en tu código de Python 
(por ejemplo: nuevo_user = User(username='mike', email='...')), 
aún no lo has mandado a la base de datos. 
La base de datos es la encargada de autogenerar ese ID (usando AUTO_INCREMENT o SERIAL).


"""
class Usuario(SQLModel, table=True):
    """
    Modelo de Usuario para la base de datos.
    Hereda de SQLModel (que combina Pydantic + SQLAlchemy)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    email: str = Field(index=True, unique=True)
    hashed_password: str = Field(min_length=8) #Ojo con esto, en producción deberías hashear la contraseña con bcrypt, proxima clase
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Configuración opcional para la tabla
        table_name = "users"