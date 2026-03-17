from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.models import AdminUser
from app.utils.security import verify_password
from app.auth import create_access_token, get_current_active_user
from app import schemas

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
async def login(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
        )

    # Sincronizar con la sesión de sqladmin para login unificado
    request.session.update(
        {"token": "authenticated", "user_id": user.id, "role": user.role or "admin"}
    )

    token = create_access_token(
        data={"sub": user.username, "role": user.role or "admin"}
    )

    # Set cookie para acceso unificado
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24,  # 24h
        samesite="lax",
        secure=False,
    )

    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: AdminUser = Depends(get_current_active_user)):
    return {"username": current_user.username, "role": current_user.role or "admin"}
