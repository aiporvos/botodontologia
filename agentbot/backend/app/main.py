from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.core.config import get_settings
from app.routers.clinic import auth, public
from app.routers.admin import patients, appointments

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    init_db()
    print("🚀 Dental Studio Pro API iniciada")
    yield
    # Shutdown
    print("👋 API detenida")


app = FastAPI(
    title="Dental Studio Pro API",
    description="API para sistema de gestión odontológica",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(public.router, prefix="/api/v1", tags=["public"])
app.include_router(patients.router, prefix="/api/v1/admin", tags=["patients"])
app.include_router(appointments.router, prefix="/api/v1/admin", tags=["appointments"])


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "dental-studio-api"}


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Dental Studio Pro API", "version": "2.0.0", "docs": "/docs"}
