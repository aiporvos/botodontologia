# Skill: Mantenimiento y Backups

## Descripción
Procedimientos de mantenimiento regular y sistema de backups para proteger los datos.

## Backups

### Tipos de backup

#### 1. Base de datos (PostgreSQL)
**Completo:**
```bash
# Backup completo
docker exec postgres pg_dump -U clinic clinic > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup comprimido
docker exec postgres pg_dump -U clinic clinic | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Incremental (si se configura WAL archiving):**
```bash
# Base + WAL logs
docker exec postgres pg_basebackup -D /backup/base -Ft -z -P
```

#### 2. Archivos estáticos
```bash
# Subidas de pacientes (fotos, radiografías, etc.)
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz /app/static/uploads/
```

#### 3. Configuración
```bash
# Variables de entorno y configuración
cp .env backup/config_$(date +%Y%m%d).env
cp docker-compose.yml backup/
```

### Automatización de backups

#### Script de backup diario
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/dental-clinic"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup de base de datos
docker exec postgres pg_dump -U clinic clinic | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup de archivos
if [ -d "/app/static/uploads" ]; then
    tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" /app/static/uploads/
fi

# Backup de config
cp .env "$BACKUP_DIR/config_$DATE.env"

# Eliminar backups antiguos
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Notificación (opcional)
echo "Backup completado: $DATE" | mail -s "Backup Dental Clinic" admin@example.com
```

#### Cron job
```bash
# Ejecutar backup todos los días a las 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

### Restauración

#### Restaurar base de datos
```bash
# Detener la aplicación
docker compose stop app

# Restaurar desde backup
docker exec -i postgres psql -U clinic -d clinic < backup_20240115.sql

# O con backup comprimido
gunzip < backup_20240115.sql.gz | docker exec -i postgres psql -U clinic -d clinic

# Reiniciar aplicación
docker compose start app
```

#### Restaurar archivos
```bash
# Extraer archivos
tar -xzf uploads_backup_20240115.tar.gz -C /app/static/
```

## Mantenimiento regular

### Semanal
- [ ] Revisar logs de errores
- [ ] Verificar espacio en disco
- [ ] Comprobar que backups se ejecutaron
- [ ] Revisar métricas de uso (CPU, RAM)

### Mensual
- [ ] Actualizar dependencias (pip packages)
- [ ] Revisar y limpiar logs viejos
- [ ] Optimizar base de datos (VACUUM ANALYZE)
- [ ] Verificar integridad de backups
- [ ] Actualizar tokens/credenciales si es necesario

### Trimestral
- [ ] Revisar permisos de archivos
- [ ] Análisis de rendimiento
- [ ] Limpiar datos temporales/archivos viejos
- [ ] Test de restauración de backup

### Anual
- [ ] Auditoría de seguridad
- [ ] Rotación de credenciales
- [ ] Revisión de contratos de servicios
- [ ] Plan de recuperación ante desastres

## Optimización

### Base de datos
```sql
-- Mantenimiento mensual
VACUUM ANALYZE;
REINDEX DATABASE clinic;

-- Ver tablas más grandes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass)) AS size
FROM pg_tables WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

### Archivos
```bash
# Limpiar archivos temporales
find /tmp -type f -atime +7 -delete

# Limpiar logs antiguos
find /var/log -name "*.log.*" -mtime +30 -delete
```

## Monitoreo

### Herramientas recomendadas
- **Uptime**: UptimeRobot o similar
- **Recursos**: Netdata o Prometheus + Grafana
- **Logs**: ELK Stack o Loki
- **Alertas**: PagerDuty o simple email

### Alertas importantes
- Base de datos no responde
- Espacio en disco > 80%
- Uso de memoria > 90%
- Errores 500 en logs
- Backup fallido

## Limpieza de datos

### Pacientes inactivos
```sql
-- Identificar pacientes sin actividad en 2 años
SELECT p.id, p.first_name, p.last_name, MAX(a.start_at) as last_appointment
FROM patients p
LEFT JOIN appointments a ON p.id = a.patient_id
WHERE a.start_at < NOW() - INTERVAL '2 years'
GROUP BY p.id
HAVING COUNT(a.id) > 0;
```

### Archivos huérfanos
```bash
# Encontrar archivos no referenciados en BD
# (requiere script personalizado según estructura)
```

## Documentación
- Mantener registro de mantenimientos realizados
- Documentar procedimientos especiales
- Versionar cambios en configuración
- Guardar contraseñas en gestor seguro (no en texto plano)
