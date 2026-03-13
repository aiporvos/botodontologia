# Notas de Actualización - Dental Studio Pro

## Cambios Realizados (13/03/2026)

### ⚠️ IMPORTANTE: Ejecutar Migraciones SQL

Antes de desplegar, ejecuta manualmente estas queries en la base de datos PostgreSQL de Dokploy:

```sql
-- Agregar columnas faltantes a la tabla appointments
ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE;

ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS reminder_sent_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS reminder_channel VARCHAR(20);

ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS confirmation_status VARCHAR(20) DEFAULT 'pending';

-- Agregar columna role a admin_users si no existe
ALTER TABLE admin_users 
ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'admin';
```

### 1. Corrección de Error en Base de Datos

Se agregó migración automática para las columnas faltantes en la tabla `appointments`:
- `reminder_sent` (BOOLEAN DEFAULT FALSE)
- `reminder_sent_at` (TIMESTAMP WITH TIME ZONE)
- `reminder_channel` (VARCHAR(20))
- `confirmation_status` (VARCHAR(20) DEFAULT 'pending')

**Archivo modificado:** `app/database.py`

Las migraciones se ejecutan automáticamente al iniciar la aplicación mediante la función `run_migrations()`.

### 2. Actualización del Token de Telegram

**Nuevo Token:** `8620574283:AAFf11ogf9ygo7-NEm58pKx3sCBn2FeORds`

**Archivo actualizado:** `.env.example`

### Configuración en Dokploy

Para que los cambios funcionen correctamente en Dokploy:

1. **Variables de Entorno**: Asegúrate de configurar en Dokploy:
   ```
   TELEGRAM_BOT_TOKEN=8620574283:AAFf11ogf9ygo7-NEm58pKx3sCBn2FeORds
   ```

2. **Base de Datos**: Las migraciones se ejecutarán automáticamente cuando se despliegue la aplicación. El sistema detectará las columnas faltantes y las agregará.

3. **Bot de Telegram**: El bot ahora usará el nuevo token y debería funcionar correctamente.

### Cómo Probar

1. **Telegram**: Busca tu bot en Telegram y envíale un mensaje como "Hola" o "Quiero agendar un turno"

2. **Verificar Logs**: En Dokploy, revisa los logs de la aplicación para ver:
   - "✅ Migraciones aplicadas" (confirmando que las columnas se agregaron)
   - "🤖 Telegram Bot Polling task created" (confirmando que el bot está activo)

### Estructura del Bot

El bot responde a solicitudes de turnos mediante:
- **AI Agent** (`app/services/ai_agent.py`): Procesa los mensajes usando OpenAI
- **Handlers** (`app/handlers/conversation.py`): Maneja las conversaciones
- **Bot Service** (`app/bot.py`): Gestiona la conexión con Telegram

### Flujo de Conversación

1. El paciente saluda o pide un turno
2. El bot pregunta el motivo de la consulta
3. Consulta disponibilidad según el tipo de tratamiento
4. Ofrece horarios disponibles
5. Solicita datos del paciente (Nombre, DNI, Obra Social, Teléfono)
6. Agenda el turno en la base de datos

### Troubleshooting

Si el bot no responde:
1. Verifica que el token esté correctamente configurado en las variables de entorno
2. Revisa los logs para errores de conexión
3. Asegúrate de que el bot no tenga un webhook antiguo configurado (el sistema lo limpia automáticamente)

### Próximos Pasos

- El sistema está listo para recibir solicitudes por Telegram
- Las columnas de recordatorios están disponibles para futuras implementaciones
- El bot puede integrarse con WhatsApp mediante Evolution API cuando esté configurada