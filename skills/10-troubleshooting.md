# Skill: Troubleshooting Comunes

## Descripción
Guía de diagnóstico y solución de problemas frecuentes en Dental Studio Pro.

## Categorías de problemas

### 1. Problemas de autenticación

#### No puedo iniciar sesión
**Síntomas:**
- "Credenciales inválidas"
- Página en blanco después de login
- Redirección infinita

**Soluciones:**
1. Verificar que el usuario admin exista en la BD
2. Resetear contraseña del admin:
   ```python
   # En Python shell o script
   from app.database import SessionLocal
   from app.utils.security import get_password_hash
   from app.models import AdminUser
   
   db = SessionLocal()
   admin = db.query(AdminUser).filter_by(username="admin").first()
   admin.password_hash = get_password_hash("admin123")
   db.commit()
   ```
3. Limpiar cookies del navegador
4. Verificar que SECRET_KEY esté configurada

### 2. Problemas de turnos

#### "No hay horarios disponibles"
**Causas:**
- No hay profesionales configurados
- No hay disponibilidad horaria definida
- Todos los slots están ocupados

**Soluciones:**
1. Crear profesionales en admin
2. Configurar horarios de disponibilidad
3. Verificar que los turnos existentes no bloqueen todo

#### Error al crear turno desde web
**Verificar:**
- Paciente seleccionado existe
- Profesional tiene disponibilidad
- No hay conflicto de horarios
- Campos obligatorios completos

**Logs:**
```bash
docker compose logs -f app | grep -i appointment
```

### 3. Problemas del Bot

#### Bot no responde
**Pasos:**
1. Verificar que TELEGRAM_BOT_TOKEN esté configurado
2. Verificar webhook: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
3. Revisar logs: `docker compose logs -f app | grep -i telegram`
4. Probar con polling si webhook falla

#### "Lo siento, no hay horarios disponibles"
**Causa:** El servicio de disponibilidad no encuentra slots

**Verificar:**
- Profesionales activos con especialidad correcta
- Horarios de disponibilidad configurados
- No hay errores en AvailabilityService

### 4. Problemas de odontograma

#### No guarda cambios
**Verificar:**
- Endpoint POST /api/patients/{id}/odontogram responde 200
- Datos enviados tienen formato correcto
- No hay errores de JavaScript en consola
- Paciente está seleccionado

#### No carga odontograma guardado
**Verificar:**
- Endpoint GET devuelve datos correctos
- Estructura JSON coincide con lo esperado
- IDs de dientes coinciden

### 5. Problemas de pagos

#### No se registra el pago
**Verificar:**
- Monto es número positivo
- Método de pago está definido
- Paciente existe
- No hay duplicados

#### Estado de cuenta no cuadra
**Causas:**
- Pagos no asociados a tratamientos
- Tratamientos sin costo definido
- Ajustes manuales sin registro

**Solución:**
Generar reporte detallado y reconciliar manualmente

### 6. Errores de base de datos

#### "column X does not exist"
**Causa:** Schema desactualizado

**Solución:**
```bash
# Regenerar tablas (cuidado: borra datos)
docker compose down
docker volume rm botodontologia_postgres_data
docker compose up -d

# O crear migración manual
```

#### Conexión rechazada
**Verificar:**
- PostgreSQL está corriendo: `docker ps | grep postgres`
- DATABASE_URL correcta
- No hay firewall bloqueando puerto 5432

### 7. Problemas de rendimiento

#### Página lenta en cargar
**Optimizaciones:**
1. Verificar queries N+1
2. Agregar índices en BD si es necesario
3. Implementar caché Redis
4. Optimizar imágenes estáticas

#### Bot responde lento
**Causas:**
- API de OpenAI lenta
- Consultas a BD pesadas
- Servidor sin recursos

### 8. Errores de despliegue

#### "port already in use"
```bash
# Ver proceso
sudo lsof -i :8000
sudo kill -9 <PID>

# O cambiar puerto en docker-compose.yml
```

#### "Cannot connect to database"
- Verificar que postgres esté healthy: `docker compose ps`
- Esperar a que BD esté lista antes de iniciar app
- Verificar red docker: `docker network ls`

#### Contenedor reiniciando constantemente
**Ver logs:**
```bash
docker compose logs -f app
```

**Causas comunes:**
- Error en entrypoint.sh
- Variable de entorno faltante
- Permisos incorrectos
- Puerto ocupado

## Comandos útiles de debugging

### Ver logs en tiempo real
```bash
# Todos los servicios
docker compose logs -f

# Solo app
docker compose logs -f app

# Con filtro
docker compose logs -f app | grep -i error
```

### Ejecutar comandos dentro del contenedor
```bash
# Shell interactiva
docker exec -it app bash

# Python shell
docker exec -it app python

# Ejecutar script
docker exec app python script.py
```

### Verificar base de datos
```bash
# Conectar a PostgreSQL
docker exec -it postgres psql -U clinic -d clinic

# Queries útiles
\dt  # Listar tablas
SELECT * FROM patients LIMIT 5;
SELECT * FROM appointments WHERE start_at > NOW();
```

### Verificar configuración
```bash
# Variables de entorno
docker exec app printenv | grep -i database

# Archivos estáticos
docker exec app ls -la static/
```

## Contacto y soporte
- Revisar issues en GitHub
- Documentación oficial
- Comunidad de desarrolladores
- Soporte técnico contratado (si aplica)

## Checklist de emergencia
Cuando todo falla:
- [ ] Verificar que Docker esté corriendo
- [ ] Verificar logs de todos los servicios
- [ ] Verificar espacio en disco
- [ ] Verificar conectividad de red
- [ ] Último backup disponible
- [ ] Plan de rollback preparado
