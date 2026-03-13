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

    # Definir migraciones SQL directas
    migrations_sql = [
        "ALTER TABLE IF EXISTS appointments ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE",
        "ALTER TABLE IF EXISTS appointments ADD COLUMN IF NOT EXISTS reminder_sent_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS appointments ADD COLUMN IF NOT EXISTS reminder_channel VARCHAR(20)",
        "ALTER TABLE IF EXISTS appointments ADD COLUMN IF NOT EXISTS confirmation_status VARCHAR(20) DEFAULT 'pending'",
        "ALTER TABLE IF EXISTS admin_users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'admin'",
    ]

    print("🔧 Ejecutando migraciones de base de datos...")

    try:
        with engine.begin() as conn:
            for sql in migrations_sql:
                try:
                    conn.execute(text(sql))
                    print(f"✅ Migración ejecutada: {sql[:60]}...")
                except Exception as e:
                    # Si la columna ya existe, el error es esperado
                    if (
                        "already exists" in str(e).lower()
                        or "duplicate column" in str(e).lower()
                    ):
                        print(f"ℹ️ Columna ya existe (skipping): {sql[:60]}...")
                    else:
                        print(f"⚠️ Error en migración: {sql[:60]}... - {e}")

        print("✅ Todas las migraciones procesadas")

    except Exception as e:
        print(f"❌ Error general en migraciones: {e}")
        import traceback

        print(traceback.format_exc())


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

    print("🗄️ Inicializando base de datos...")

    # Crear todas las tablas
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas/verificadas")
    except Exception as e:
        print(f"⚠️ Error creando tablas: {e}")

    # Aplicar migraciones para columnas nuevas
    run_migrations()


# Ejecutar migraciones al importar el módulo
print("🚀 Cargando módulo de base de datos...")
