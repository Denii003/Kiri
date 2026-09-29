# core/security.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from core.config import settings

# Configuración para Argon2
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=10240,
    argon2__parallelism=2,
)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_password_hash(password: str) -> str:
    """Hashea la contraseña usando Argon2."""
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    return pwd_context.verify(
        plain_password,
        hashed_password
    )