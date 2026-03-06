# Estructura del Proyecto

```
botodontologia/
├── app/                          # Aplicación principal
│   ├── __init__.py
│   ├── main.py                   # FastAPI app y rutas
│   ├── admin.py                  # Configuración SQLAdmin
│   ├── bot.py                    # Configuración bot Telegram
│   ├── database.py               # Conexión y configuración BD
│   │
│   ├── models/                   # Modelos SQLAlchemy
│   │   └── __init__.py          # Todos los modelos
│   │       ├── Patient           # Pacientes
│   │       ├── Professional      # Profesionales/Dentistas
│   │       ├── Appointment       # Turnos/Citas
│   │       ├── Availability      # Disponibilidad
│   │       ├── DentalRecord      # Registros dentales
│   │       ├── DentalTreatment   # Tratamientos
│   │       ├── Payment           # Pagos
│   │       ├── Debt              # Deudas
│   │       ├── Consent           # Consentimientos
│   │       ├── ChatSession      # Sesiones de chat
│   │       ├── AdminUser        # Usuarios admin
│   │       └── TreatmentPrice   # Precios tratamientos
│   │
│   ├── handlers/                 # Handlers del bot
│   │   └── conversation.py       # Conversaciones Telegram
│   │
│   └── services/                 # Servicios externos
│       ├── telegram.py          # Integración Telegram
│       ├── evolution.py         # Evolution API (WhatsApp)
│       └── cal_com.py           # Cal.com API
│
├── config.py                     # Configuración global
├── requirements.txt              # Dependencias Python
├── Dockerfile                    # Imagen Docker
├── docker-compose.yml            # Servicios Docker
├── .env.example                  # Ejemplo variables entorno
│
├── templates/                    # Plantillas HTML
│   ├── dashboard.html
│   ├── odontogram.html
│   └── payments.html
│
├── static/                      # Archivos estáticos
│   └── (vacío - CSS/JS del admin)
│
├── images/                      # Imágenes del proyecto
└── docs/                       # Documentación
    ├── README.md
    ├── ESTRUCTURA.md
    ├── CONFIGURACION.md
    ├── DESPLIEGUE.md
    ├── API.md
    ├── MODELOS.md
    ├── DOCKER.md
    └── TROUBLESHOOTING.md
```

## Descripción de Módulos

### app/main.py
Punto de entrada de la aplicación FastAPI. Contiene:
- Configuración de la app
- Rutas de la API REST
- Webhooks para Telegram y WhatsApp
- Inicialización de base de datos

### app/admin.py
Configuración del panel de administración SQLAdmin:
- Modelos visibles
- Columnas a mostrar
- Permisos de edición/creación/borrado

### app/bot.py
Configuración del bot de Telegram:
- Dispatcher de aiogram
- Registro de handlers
- Configuración de comandos

### app/database.py
Conexión a PostgreSQL:
- Engine de SQLAlchemy
- SessionLocal
- Función init_db() para crear tablas

### app/models/
Contiene todos los modelos de la base de datos usando SQLAlchemy ORM.

## Flujo de Datos

```
Usuario → Telegram/WhatsApp → Webhook → Handler → Database
                                    ↓
                              Cal.com API
                              Evolution API
```

## Archivos de Configuración

| Archivo | Propósito |
|---------|-----------|
| config.py | Configuración de la aplicación |
| .env.example | Variables de entorno template |
| docker-compose.yml | Servicios Docker |
| Dockerfile | Imagen de la aplicación |
