from fastapi import FastAPI
import asyncio
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from config import settings
from app.database import engine, init_db, SessionLocal
from app.admin import setup_admin
from app.models import AdminUser, Professional, Availability
from app.utils.security import get_password_hash

# Importación de Routers
from app.routers import (
    auth, 
    patients, 
    appointments, 
    stats, 
    odontogram, 
    payments, 
    catalog, 
    webhooks,
    pages
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("📦 Inicializando base de datos...")
    init_db()

    db = SessionLocal()
    try:
        # Asegurar usuario admin
        admin = (
            db.query(AdminUser)
            .filter(AdminUser.username == settings.admin_username)
            .first()
        )
        if not admin:
            admin = AdminUser(
                username=settings.admin_username,
                password_hash=get_password_hash(settings.admin_password),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin creado: {settings.admin_username}")
        else:
            admin.password_hash = get_password_hash(settings.admin_password)
            admin.role = "admin"
            admin.is_active = True
            db.commit()
            print("🔄 Usuario admin sincronizado")

        # Profesionales por defecto
        if db.query(Professional).count() == 0:
            prof1 = Professional(
                full_name="Dr. Silvestro",
                specialty="extracciones/implantes/protesis",
            )
            prof2 = Professional(
                full_name="Dra. Murad", specialty="ortodoncia/conductos"
            )
            db.add_all([prof1, prof2])
            db.commit()

            from datetime import time
            for prof in [prof1, prof2]:
                for day in range(1, 6): # Lunes a Viernes
                    availability = Availability(
                        professional_id=prof.id,
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(18, 0),
                        slot_minutes=30,
                    )
                    db.add(availability)
            db.commit()
            print("✅ Profesionales creados con horarios de disponibilidad")
    finally:
        db.close()

    # Iniciar Bot de Telegram
    from app.bot import start_bot
    if settings.telegram_bot_token:
        asyncio.create_task(start_bot())
        print("🤖 Telegram Bot Polling task created")

    print("🚀 Dental Studio Pro iniciado")
    yield

app = FastAPI(
    title="Dental Studio Pro",
    description="Sistema de gestión odontológica modular",
    version="2.1.0",
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(SessionMiddleware, secret_key="dental-studio-super-secret-key-123")
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# Estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Admin Panel
setup_admin(app, engine)

# Inclusión de Routers
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(stats.router)
app.include_router(odontogram.router)
app.include_router(payments.router)
app.include_router(catalog.router)
app.include_router(webhooks.router)
