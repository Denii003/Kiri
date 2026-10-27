# db/database.py
from sqlmodel import Session, SQLModel, create_engine

from core.config import settings
import models  # noqa: F401  (registra todas las tablas en SQLModel.metadata)

DATABASE_URL = settings.DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
