from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy.orm import declarative_base

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    from app.models import (
        Patient,
        Professional,
        Availability,
        Appointment,
        DentalRecord,
        Consent,
        ChatSession,
        AdminUser,
        Payment,
        Debt,
        DentalTreatment,
    )

    Base.metadata.create_all(bind=engine)
