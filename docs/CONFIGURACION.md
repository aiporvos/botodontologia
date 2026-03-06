# Configuración

## Variables de Entorno

Copia `.env.example` a `.env` y configura los valores.

### Base de Datos

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de conexión PostgreSQL | `postgresql://clinic:clinicpass@postgres:5432/clinic` |
| `DB_PASSWORD` | Contraseña PostgreSQL | `clinicpass` |

### Bot de Telegram

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `BOT_SECRET` | Secret para verificación | `tu_secret_seguro` |

### Cal.com (Reservas)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `CALCOM_URL` | URL de la instancia Cal.com | `https://odontologia.aiporvos.com` |
| `CALCOM_API_KEY` | API Key de Cal.com | `cal_live_...` |

### Evolution API (WhatsApp)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `EVOLUTION_URL` | URL del servidor Evolution | `http://evolution-api:8080` |
| `EVOLUTION_API_KEY` | API Key de Evolution | `tu_api_key` |
| `EVOLUTION_INSTANCE_NAME` | Nombre de la instancia | `clinic` |
| `EVOLUTION_INSTANCE_TOKEN` | Token de la instancia | `tu_token` |

### Aplicación

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DEBUG` | Modo debug | `true` |
| `ADMIN_USERNAME` | Usuario admin | `admin` |
| `ADMIN_PASSWORD` | Contraseña admin | `admin123` |
| `APP_HOST` | Host de la app | `0.0.0.0` |
| `APP_PORT` | Puerto de la app | `8000` |

## config.py

El archivo `config.py` usa Pydantic Settings para manejar la configuración:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    db_host: str = "postgres"
    db_port: int = 5432
    db_user: str = "clinic"
    db_password: str = "clinicpass"
    db_name: str = "clinic"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    # ... más configuración
```

## Desarrollo Local

```bash
# Crear archivo .env
cp .env.example .env

# Editar con tus valores
nano .env
```

## Producción

En Dokploy, las variables se configuran en la sección **Environment** del proyecto.

### Variables Obligatorias

Para que la app funcione:
- `DB_PASSWORD` = `clinicpass` (o la que uses en docker-compose)

### Variables Opcionales

- `TELEGRAM_BOT_TOKEN` - Para bot de Telegram
- `BOT_SECRET` - Secret del bot
- `CALCOM_URL` / `CALCOM_API_KEY` - Para reservas
- `EVOLUTION_*` - Para WhatsApp
- `ADMIN_PASSWORD` - Contraseña del admin
