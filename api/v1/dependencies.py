from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from sqlmodel import Session,select 

from db.database import get_session
from core.config import settings
from models.user_model import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/token")
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
) ->Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    statement = select(Usuario).where(Usuario.username == username)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user
async def get_current_activate_user(
        current_user: Usuario = Depends(get_current_user)
) ->Usuario:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="usuario inactivo"
        )
    return current_user