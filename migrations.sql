-- Migraciones para Dental Studio Pro
-- Ejecutar estas queries directamente en la base de datos PostgreSQL

-- 1. Agregar columnas faltantes a la tabla appointments
ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE;

ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS reminder_sent_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS reminder_channel VARCHAR(20);

ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS confirmation_status VARCHAR(20) DEFAULT 'pending';

-- 2. Agregar columna role a admin_users si no existe
ALTER TABLE admin_users 
ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'admin';

-- Verificar que las columnas se agregaron correctamente
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'appointments'
AND column_name IN ('reminder_sent', 'reminder_sent_at', 'reminder_channel', 'confirmation_status');