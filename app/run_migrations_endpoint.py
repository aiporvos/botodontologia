"""
Endpoint temporal para ejecutar migraciones
ELIMINAR DESPUÉS DE USAR
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.database import engine
import traceback

router = APIRouter()


@router.get("/api/run-migrations-temp")
async def run_migrations_temp():
    """
    Endpoint temporal para ejecutar migraciones SQL
    IMPORTANTE: Eliminar este endpoint después de usarlo
    """
    migrations = [
        """ALTER TABLE appointments 
           ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE""",
        """ALTER TABLE appointments 
           ADD COLUMN IF NOT EXISTS reminder_sent_at TIMESTAMP WITH TIME ZONE""",
        """ALTER TABLE appointments 
           ADD COLUMN IF NOT EXISTS reminder_channel VARCHAR(20)""",
        """ALTER TABLE appointments 
           ADD COLUMN IF NOT EXISTS confirmation_status VARCHAR(20) DEFAULT 'pending'""",
        """ALTER TABLE admin_users 
           ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'admin'""",
    ]

    results = []

    with engine.begin() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                results.append(f"✅ Ejecutado: {sql[:50]}...")
            except Exception as e:
                results.append(f"❌ Error: {sql[:50]}... - {str(e)}")

    return {
        "status": "completed",
        "results": results,
        "message": "IMPORTANTE: Elimina este endpoint del código después de usarlo",
    }


@router.get("/api/check-columns-temp")
async def check_columns_temp():
    """Verifica qué columnas existen en la tabla appointments"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'appointments'
                ORDER BY ordinal_position
            """)
            )
            columns = [dict(row._mapping) for row in result]

        return {
            "table": "appointments",
            "columns": columns,
            "has_reminder_sent": any(
                c["column_name"] == "reminder_sent" for c in columns
            ),
            "has_reminder_sent_at": any(
                c["column_name"] == "reminder_sent_at" for c in columns
            ),
            "has_reminder_channel": any(
                c["column_name"] == "reminder_channel" for c in columns
            ),
            "has_confirmation_status": any(
                c["column_name"] == "confirmation_status" for c in columns
            ),
        }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}
