# api/v1/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from core.config import settings
from db.database import get_session
from models.user_model import Usuario
from schemas.token_schema import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(username=payload.get("sub"))
    except JWTError:
        raise credentials_exception
    if token_data.username is None:
        raise credentials_exception

    user = session.exec(select(Usuario).where(Usuario.username == token_data.username)).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return current_user
