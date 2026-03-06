from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from config import settings
from app.models import Base

engine = create_engine(settings.database_url, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Aplica migraciones simples para columnas faltantes en tablas existentes"""
    inspector = inspect(engine)
    
    migrations = [
        {
            "table": "admin_users",
            "column": "role",
            "sql": "ALTER TABLE admin_users ADD COLUMN role VARCHAR(20) DEFAULT 'admin'"
        },
    ]
    
    with engine.connect() as conn:
        for m in migrations:
            if inspector.has_table(m["table"]):
                columns = [c["name"] for c in inspector.get_columns(m["table"])]
                if m["column"] not in columns:
                    print(f"🔧 Migrando: agregando columna '{m['column']}' a '{m['table']}'")
                    conn.execute(text(m["sql"]))
                    conn.commit()


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
    print("✅ Tablas creadas/verificadas")
    
    # Aplicar migraciones para columnas nuevas en tablas existentes
    run_migrations()
    print("✅ Migraciones aplicadas")
