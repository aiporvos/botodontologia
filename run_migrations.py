#!/usr/bin/env python3
"""Script para ejecutar las migraciones de la base de datos"""

from app.database import run_migrations, engine
from sqlalchemy import inspect


def main():
    print("🚀 Ejecutando migraciones de base de datos...")

    # Verificar estado actual de la tabla appointments
    inspector = inspect(engine)
    if inspector.has_table("appointments"):
        columns = [c["name"] for c in inspector.get_columns("appointments")]
        print(f"\n📊 Columnas actuales en tabla 'appointments':")
        for col in sorted(columns):
            print(f"   - {col}")

    # Ejecutar migraciones
    run_migrations()

    # Verificar estado después de las migraciones
    if inspector.has_table("appointments"):
        columns_after = [c["name"] for c in inspector.get_columns("appointments")]
        print(f"\n✅ Columnas después de las migraciones:")
        for col in sorted(columns_after):
            print(f"   - {col}")

    print("\n✨ Migraciones completadas con éxito!")


if __name__ == "__main__":
    main()
