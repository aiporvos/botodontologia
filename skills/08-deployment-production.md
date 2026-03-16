# Skill: Despliegue en Producción

## Descripción
Guía completa para desplegar Dental Studio Pro en un servidor de producción.

## Requisitos del servidor

### Hardware mínimo
- 2 vCPU
- 4GB RAM
- 20GB SSD

### Software requerido
- Docker y Docker Compose
- Git
- Nginx (reverse proxy)
- SSL Certificate (Let's Encrypt)

## Configuración de variables de entorno

### Obligatorias
```
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/clinic

# Bot
TELEGRAM_BOT_TOKEN=tu_token_aqui

# OpenAI (para bot inteligente)
OPENAI_API_KEY=sk-...

# Seguridad
SECRET_KEY=clave_secreta_larga_y_aleatoria
```

### Opcionales
```
# Cal.com integration
CALCOM_API_KEY=...
CALCOM_WEBHOOK_SECRET=...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...

# WhatsApp (Evolution API)
EVOLUTION_URL=http://evolution:8080
EVOLUTION_API_KEY=...
```

## Pasos de despliegue

### 1. Preparar el servidor
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose-plugin

# Configurar Git
git config --global user.email "admin@example.com"
git config --global user.name "Admin"
```

### 2. Clonar y configurar
```bash
git clone https://github.com/aiporvos/botodontologia.git
cd botodontologia

# Crear archivo .env
nano .env  # Configurar todas las variables

# Crear directorios persistentes
mkdir -p postgres_data static/uploads
```

### 3. Iniciar servicios
```bash
# Construir e iniciar
docker compose up -d --build

# Verificar logs
docker compose logs -f app

# Verificar base de datos
docker compose logs -f postgres
```

### 4. Configurar Nginx (reverse proxy)
```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 5. SSL con Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

### 6. Configurar Webhook de Telegram
```bash
curl -F "url=https://tu-dominio.com/webhook/telegram" \
     -F "drop_pending_updates=true" \
     https://api.telegram.org/bot<TOKEN>/setWebhook
```

## Monitoreo y mantenimiento

### Health checks
- Verificar que todos los contenedores estén corriendo: `docker ps`
- Revisar uso de recursos: `docker stats`
- Logs en tiempo real: `docker compose logs -f`

### Backups automáticos
```bash
# Backup diario de PostgreSQL
0 2 * * * /usr/bin/docker exec postgres pg_dump -U clinic clinic > /backup/clinic_$(date +\%Y\%m\%d).sql

# Backup de archivos estáticos
0 3 * * * tar -czf /backup/uploads_$(date +\%Y\%m\%d).tar.gz /var/lib/docker/volumes/uploads/_data
```

### Actualizaciones
```bash
# Actualizar código
git pull origin main

# Reconstruir y reiniciar
docker compose down
docker compose up -d --build

# Migraciones automáticas (ya están en el entrypoint)
```

## Troubleshooting comunes

### Error: "port already in use"
```bash
sudo lsof -i :8000  # Ver qué proceso usa el puerto
sudo kill -9 <PID>   # Matar proceso
```

### Error de conexión a base de datos
- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en DATABASE_URL
- Verificar que la red docker esté creada

### Bot no responde
- Verificar TELEGRAM_BOT_TOKEN
- Verificar webhook configurado correctamente
- Revisar logs: `docker compose logs -f app | grep -i bot`

### Archivos estáticos no cargan
- Verificar Nginx configuración
- Verificar permisos de directorio
- Revisar logs de Nginx: `sudo tail -f /var/log/nginx/error.log`

## Consideraciones de seguridad
- Cambiar contraseña default admin
- Deshabilitar modo debug en producción
- Configurar firewall (ufw)
- Actualizaciones de seguridad automáticas
- Logs de auditoría
- Rate limiting en Nginx

## Escalabilidad
- Puedes escalar horizontalmente con múltiples workers
- Considerar Redis para caché y sesiones
- Load balancer si hay mucho tráfico
