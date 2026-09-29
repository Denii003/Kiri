# db/database.py
import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Obtiene la URL de la base de datos. 
# Si no existe, usa SQLite por defecto para no romper el entorno local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mikedb.db")

# Configuración del motor
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, 
    echo=False,  # En producción siempre False
    connect_args=connect_args
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session