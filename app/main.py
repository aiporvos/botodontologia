from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from config import settings
from app.database import engine, init_db, SessionLocal, get_db
from app.admin import setup_admin
from app.handlers.conversation import handle_whatsapp_message
from app.models import Patient, Appointment, Professional, AdminUser
from app.utils.security import get_password_hash, verify_password
from app.auth import create_access_token, get_current_active_user
from app import schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización al iniciar la app"""
    print("📦 Inicializando base de datos...")
    init_db()

    # Crear admin por defecto o actualizar su hash
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == settings.admin_username).first()
        if not admin:
            hashed_pw = get_password_hash(settings.admin_password)
            admin = AdminUser(
                username=settings.admin_username, 
                password_hash=hashed_pw,
                role="admin"
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin creado: {settings.admin_username}")
        else:
            # Re-hashear si el hash no es pbkdf2_sha256
            if not admin.password_hash.startswith("$pbkdf2"):
                admin.password_hash = get_password_hash(settings.admin_password)
                db.commit()
                print("🔄 Contraseña de admin actualizada")
    finally:
        db.close()
    
    yield

app = FastAPI(
    title="Dental Studio Pro",
    description="Sistema de gestión odontológica de última generación",
    version="2.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
setup_admin(app, engine)

# ==================== RUTAS DE INTERFAZ ====================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard_v2.html", {"request": request})

# ==================== AUTENTICACIÓN ====================

@app.post("/api/auth/login", response_model=schemas.Token)
async def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ==================== API PROTEGIDA ====================

@app.get("/api/patients", response_model=List[schemas.Patient])
async def list_patients(
    db: Session = Depends(get_db), 
    current_user: AdminUser = Depends(get_current_active_user)
):
    return db.query(Patient).all()

@app.get("/api/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user)
):
    from sqlalchemy import func
    return {
        "patients": db.query(func.count(Patient.id)).scalar() or 0,
        "appointments": db.query(func.count(Appointment.id)).scalar() or 0,
        "revenue": 45000 # Simulado para el dashboard
    }

# ==================== WEBHOOKS ====================

@app.post("/webhook")
async def webhook_evolution(request: Request):
    try:
        data = await request.json()
        messages = data.get("data", {}).get("messages", [])
        for msg in messages:
            if msg.get("type") in ["conversation", "text"]:
                text = msg.get("body", {}).get("text", {}).get("text", "")
                from_num = msg.get("key", {}).get("remoteJid", "").split("@")[0]
                if text and from_num:
                    await handle_whatsapp_message(from_num, text)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/webhook/telegram")
async def webhook_telegram(request: Request):
    try:
        from app.bot import dp, bot
        from aiogram.types import Update
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot=bot, update=update)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
