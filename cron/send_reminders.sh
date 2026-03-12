#!/bin/bash
# Cron job para enviar recordatorios de turnos
# Ejemplo de configuración en crontab:
# 0 9 * * * /home/user/botodontologia/cron/send_reminders.sh
# (Ejecuta todos los días a las 9:00 AM)

# Navegar al directorio del proyecto
cd /home/user/botodontologia

# Activar entorno virtual (ajustar ruta según corresponda)
source venv/bin/activate

# Ejecutar script de recordatorios
python -m app.services.reminders

# Desactivar entorno
deactivate
