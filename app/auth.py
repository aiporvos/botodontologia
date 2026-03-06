from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from config import settings
from app.database import get_db
from app.models import AdminUser

# Configuración JWT
SECRET_KEY = settings.admin_password # Usamos un secreto de config
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 horas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Optional[HTTPException] = None, db: Session = Depends(get_db)):
    # Importamos dinámicamente para evitar dependencias circulares si las hubiera
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    
    # Esta función ahora es más flexible para manejar header O cookie
    # Necesitamos acceder al request de forma manual si es posible
    # (FastAPI no nos da el request directamente en una dependencia si no lo pedimos)
    # Así que usamos una aproximación simplificada:
    pass

# Versión simplificada y funcional
async def get_current_user_logic(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Intentar obtener token del Header
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # 2. Intentar obtener token de Cookie si no hay header
    if not token:
        token = request.cookies.get("access_token")
        
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: AdminUser = Depends(get_current_user_logic)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user
