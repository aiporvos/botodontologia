# Guía de Despliegue

Este documento explica cómo desplegar el proyecto en Dokploy.

## Requisitos

- Servidor con Dokploy instalado
- Dominio (opcional)
- GitHub conectado a Dokploy

## Pasos

### 1. Preparar el Repositorio

Asegúrate de que el código esté en GitHub:
```bash
git push origin main
```

### 2. Crear Proyecto en Dokploy

1. Ve al panel de Dokploy
2. Crea un nuevo **Project**
3. Nombre: `Clínica Dental` (o el que prefieras)

### 3. Crear Servicio (Compose)

1. En el proyecto, selecciona **Create Service**
2. Elige tipo **Compose** (no Application)
3. Configura:
   - **Name**: `clinic-app`
   - **Git Repository**: Selecciona tu repositorio GitHub
   - **Branch**: `main`
   - **Build Path**: `/`

### 4. Configurar Variables de Entorno

En la sección **Environment** del servicio, agrega:

| Variable | Valor |
|----------|-------|
| `DB_PASSWORD` | `clinicpass` |
| `TELEGRAM_BOT_TOKEN` | *(tu token)* |
| `BOT_SECRET` | *(genera uno)* |
| `ADMIN_PASSWORD` | *(tu password)* |

### 5. Configurar Dominio (Opcional)

1. Ve a la sección **Domains**
2. Agrega tu dominio:
   - **Domain**: `odobot.aiporvos.com`
   - **Path**: `/`
   - **Port**: `8000`
   - **HTTPS**: Enabled (Let's Encrypt)

### 6. Deploy

1. Click en **Deploy**
2. Espera a que termine el build
3. Revisa los **Logs** para verificar que todo OK

## Estructura Docker Compose

El proyecto usa `docker-compose.yml` que incluye:

```yaml
services:
  clinic-app:      # Aplicación Python/FastAPI
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      # ... más vars
    depends_on:
      - postgres

  postgres:        # Base de datos
    image: postgres:16
    environment:
      POSTGRES_USER: clinic
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: clinic
    volumes:
      - pgdata:/var/lib/postgresql/data
```

## Puertos

| Servicio | Puerto |
|----------|--------|
| App | 8000 |
| PostgreSQL | 5432 (interno) |

## Verificar Funcionamiento

1. **App principal**: `http://tu-dominio/`
2. **Admin**: `http://tu-dominio/admin`
3. **API Docs**: `http://tu-dominio/docs`

## Troubleshooting

### Error: Bad Gateway
- Verifica que el puerto sea **8000** (no 80)

### Error: DATABASE_URL vacía
- Asegúrate de tener `DB_PASSWORD` configurado en Environment

### Error: No space left on device
- Limpia el servidor: `docker system prune -a`

### Error: Module not found
- Fuerza un rebuild en Dokploy (Clean Build)

## Actualizar Después de Cambios

```bash
git add .
git commit -m "tu mensaje"
git push origin main
```

Dokploy detectará el cambio y hará redeploy automáticamente.

## Backup

Dokploy puede hacer backups automáticos. Configúralo en la sección **Backups** del servicio.
