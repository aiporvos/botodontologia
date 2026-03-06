# Clínica Dental - Botodontologia

Sistema de gestión para consultorio odontológico con bot de Telegram y WhatsApp.

## Características

- **Panel de Administración**: Interfaz web para gestionar pacientes, turnos, tratamientos
- **Bot de Telegram**: Asistente virtual para gestionar turnos
- **Bot de WhatsApp**: Integración con Evolution API
- **Integración con Cal.com**: Sistema de reservas online
- **Base de datos PostgreSQL**: Almacenamiento persistente
- **API REST**: Endpoints para integración externa

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Bot**: Aiogram 3 (Telegram)
- **Admin**: SQLAdmin
- **Despliegue**: Docker + Dokploy

## Inicio Rápido

### Requisitos

- Python 3.11+
- Docker y Docker Compose
- PostgreSQL (local o remoto)

### Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/aiporvos/botodontologia.git
cd botodontologia

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 5. Iniciar base de datos (Docker)
docker run -d -p 5432:5432 -e POSTGRES_USER=clinic -e POSTGRES_PASSWORD=clinicpass -e POSTGRES_DB=clinic --name postgres postgres:16

# 6. Ejecutar aplicación
uvicorn app.main:app --reload
```

### Con Docker Compose

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## URLs de Acceso

- **Web**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs

## Credenciales por Defecto

- **Usuario**: admin
- **Contraseña**: admin123

## Estructura del Proyecto

```
├── app/
│   ├── main.py           # Aplicación FastAPI principal
│   ├── admin.py          # Configuración del panel admin
│   ├── bot.py            # Configuración del bot de Telegram
│   ├── database.py       # Conexión a base de datos
│   ├── models/           # Modelos SQLAlchemy
│   │   └── __init__.py
│   ├── handlers/         # Handlers del bot
│   └── services/         # Servicios externos
├── config.py             # Configuración de la app
├── docker-compose.yml    # Servicios Docker
├── Dockerfile            # Imagen Docker de la app
├── requirements.txt      # Dependencias Python
└── templates/            # Plantillas HTML
```

## Despliegue en Producción

Ver [DESPLIEGUE.md](./DESPLIEGUE.md) para instrucciones detalladas.

### Resumen Dokploy

1. Crear proyecto en Dokploy
2. Conectar repositorio GitHub
3. Usar tipo **Compose** para会自动 include PostgreSQL
4. Configurar variables de entorno
5. Deploy

## Variables de Entorno

Ver [CONFIGURACION.md](./CONFIGURACION.md) para lista completa.

## API REST

Ver [API.md](./API.md) para documentación de endpoints.

## Modelo de Datos

Ver [MODELOS.md](./MODELOS.md) para esquema de base de datos.

## Solución de Problemas

Ver [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) para problemas comunes.

## Contributing

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -m 'Add nueva caracteristica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Licencia

MIT
