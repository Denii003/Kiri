# main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.todo_api import router_todo
from api.v1.user_api import router as users_router
from core.cors import setup_cors
from core.storage import ensure_bucket
from db.database import create_db_and_tables

logger = logging.getLogger("kiri")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando base de datos...")
    create_db_and_tables()
    try:
        ensure_bucket()
    except Exception as exc:  # MinIO apagado no debe impedir que la API arranque
        logger.warning("MinIO no disponible al iniciar: %s", exc)
    yield
    # Shutdown
    logger.info("Cerrando aplicación...")


app = FastAPI(
    title="KIRI API",
    description="Backend de KIRI: usuarios, autenticación JWT, refrigeradores y almacenamiento en MinIO",
    version="0.1.0",
    lifespan=lifespan,
)

setup_cors(app)

app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(router_todo, prefix="/api/v1", tags=["Refrigeradores"])


@app.get("/")
def root():
    return {"message": "¡Bienvenido a KIRI!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
