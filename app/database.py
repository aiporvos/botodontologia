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
            "sql": "ALTER TABLE admin_users ADD COLUMN role VARCHAR(20) DEFAULT 'admin'",
        },
        {
            "table": "appointments",
            "column": "reminder_sent",
            "sql": "ALTER TABLE appointments ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE",
        },
        {
            "table": "appointments",
            "column": "reminder_sent_at",
            "sql": "ALTER TABLE appointments ADD COLUMN reminder_sent_at TIMESTAMP WITH TIME ZONE",
        },
        {
            "table": "appointments",
            "column": "reminder_channel",
            "sql": "ALTER TABLE appointments ADD COLUMN reminder_channel VARCHAR(20)",
        },
        {
            "table": "appointments",
            "column": "confirmation_status",
            "sql": "ALTER TABLE appointments ADD COLUMN confirmation_status VARCHAR(20) DEFAULT 'pending'",
        },
    ]

    with (
        engine.begin() as conn
    ):  # Usar begin() para manejar transacciones automáticamente
        for m in migrations:
            try:
                if inspector.has_table(m["table"]):
                    columns = [c["name"] for c in inspector.get_columns(m["table"])]
                    if m["column"] not in columns:
                        print(
                            f"🔧 Migrando: agregando columna '{m['column']}' a '{m['table']}'"
                        )
                        conn.execute(text(m["sql"]))
                        print(f"✅ Columna '{m['column']}' agregada exitosamente")
            except Exception as e:
                print(
                    f"⚠️ Error al migrar columna '{m['column']}' en '{m['table']}': {e}"
                )
                # Continuar con las siguientes migraciones


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
