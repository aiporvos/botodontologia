# Sistema de Gestión de Clínica Dental

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Instalación Local (Desarrollo)](#instalación-local-desarrollo)
4. [Configuración en Dokploy](#configuración-en-dokploy)
5. [Configuración de Servicios Externos](#configuración-de-servicios-externos)
6. [Uso del Sistema](#uso-del-sistema)
7. [APIs Disponibles](#apis-disponibles)
8. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

Antes de comenzar, necesitas tener instalado:

- **Docker** y **Docker Compose**
- **Git** (para clonar el repositorio)
- Acceso a **Dokploy** (ya configurado)
- Cuenta de **Telegram** (para crear el bot)
- Acceso a **Cal.com** (ya instalado)
- **Evolution API** corriendo (ya instalado)

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DOKPLOY                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────┐  ┌─────────────────────────────────┐│
│  │   Cal.com      │  │ PostgreSQL  │  │   App Python                    ││
│  │   :3000        │  │  :5432      │  │   - Bot (aiogram)  :8000       ││
│  │                 │  │             │  │   - Admin (SQLAdmin)            ││
│  └─────────────────┘  └─────────────┘  └─────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Evolution API (WhatsApp) :8080                                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Dominios:                                                                  │
│  - odontologia.aiporvos.com (Cal.com)                                       │
│  - botodontologia.aiporvos.com (App Python)                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Componentes

| Componente | Tecnología | Función |
|------------|-----------|---------|
| **Bot** | Python + aiogram | Maneja turnos por WhatsApp y Telegram |
| **Admin Web** | FastAPI + SQLAdmin | Panel de administración |
| **DB** | PostgreSQL | Almacena pacientes, turnos, registros |
| **WhatsApp** | Evolution API | Conexión con WhatsApp |
| **Agenda** | Cal.com | Gestión de turnos y agenda |

---

## Instalación Local (Desarrollo)

### 1. Clonar el Proyecto

```bash
cd /home/cluna/Documentos/5-IA
git clone <URL-DEL-REPOSITORIO> clinic-app
cd clinic-app
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
nano .env
```

Edita el archivo `.env` con tus valores:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
BOT_SECRET=random_string_segura

# Database
DATABASE_URL=postgresql://clinic:tu_password@localhost:5432/clinic
DB_PASSWORD=tu_password_seguro

# Cal.com
CALCOM_URL=https://odontologia.aiporvos.com
CALCOM_API_KEY=tu_calcom_api_key

# Evolution API (WhatsApp)
EVOLUTION_URL=http://localhost:8080
EVOLUTION_API_KEY=tu_api_key_evolution
EVOLUTION_INSTANCE_NAME=clinic
EVOLUTION_INSTANCE_TOKEN=tu_instance_token

# Admin
ADMIN_PASSWORD=admin123
```

### 3. Instalar Dependencias (Opcional - para desarrollo local sin Docker)

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Ejecutar con Docker Compose

```bash
docker-compose up -d
```

Esto levantará:
- La aplicación en `http://localhost:8000`
- PostgreSQL en el puerto `5432`

### 5. Verificar que Funciona

- **App Principal**: http://localhost:8000
- **Dashboard**: http://localhost:8000/dashboard
- **Admin**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs

---

## Configuración en Dokploy

### Paso 1: Subir el Código a Git

```bash
git add .
git commit -m "Initial commit"
git remote add origin <URL-DEL-REPOSITORIO>
git push -u origin main
```

### Paso 2: Crear la Aplicación en Dokploy

1. Ve a tu panel de Dokploy
2. Crea una nueva aplicación
3. Selecciona **Docker Compose**
4. Configura:
   - **Nombre**: clinic-app
   - **Puerto**: 8000
   - **Rama**: main
   - **Build**: Dockerfile

### Paso 3: Configurar Variables de Entorno

En Dokploy, configura las siguientes variables:

| Variable | Valor |
|----------|-------|
| `TELEGRAM_BOT_TOKEN` | Token de tu bot de Telegram |
| `BOT_SECRET` | Una cadena aleatoria segura |
| `DATABASE_URL` | postgresql://clinic:password@host:5432/clinic |
| `CALCOM_URL` | https://odontologia.aiporvos.com |
| `CALCOM_API_KEY` | Tu API key de Cal.com |
| `EVOLUTION_URL` | http://evolution-api:8080 |
| `EVOLUTION_API_KEY` | Tu API key de Evolution |
| `EVOLUTION_INSTANCE_NAME` | clinic |
| `EVOLUTION_INSTANCE_TOKEN` | Tu token de instancia |
| `ADMIN_PASSWORD` | Tu contraseña de admin |

### Paso 4: Configurar el Dominio

1. Crea un subdominio: `botodontologia.aiporvos.com`
2. Apúntalo al puerto 8000 de tu aplicación
3. Asegúrate de tener HTTPS habilitado

---

## Configuración de Servicios Externos

### 1. Telegram Bot

1. Abre **@BotFather** en Telegram
2. Envía `/newbot`
3. Sigue las instrucciones y ponle un nombre
4. Te dará un **Token** (algo como `123456:ABC-DEF...`)
5. Copia ese token a la variable `TELEGRAM_BOT_TOKEN`

### 2. Cal.com

1. Ve a tu Cal.com: https://odontologia.aiporvos.com
2. Inicia sesión
3. Ve a **Settings** → **API Keys**
4. Crea una nueva API Key
5. Copia la key a `CALCOM_API_KEY`

### 3. Evolution API (WhatsApp)

1. Ya tienes Evolution API corriendo
2. Crea una nueva instancia:
   - Ve a la UI de Evolution API
   - Crea una instancia llamada "clinic"
3. Escanea el QR con tu WhatsApp
4. Copia el **Instance Token** a `EVOLUTION_INSTANCE_TOKEN`
5. Copia el **API Key** a `EVOLUTION_API_KEY`

### 4. Configurar Webhook de WhatsApp

Una vez que tengas la app corriendo:

1. Ve a la UI de Evolution API
2. Busca la configuración de Webhook
3. Configura la URL:
   ```
   https://botodontologia.aiporvos.com/webhook
   ```
4. Activa los eventos: `MESSAGES_UPSERT`

---

## Uso del Sistema

### Para Pacientes

#### Por WhatsApp
1. El paciente te escribe por WhatsApp
2. El bot responde automáticamente
3. Flujo:
   - "Hola" → El bot da la bienvenida
   - "TURNO" → Inicia solicitud de turno
   - Pide: Nombre → Obra Social → Motivo → Teléfono
   - Ofrece horarios disponibles
   - Confirma el turno

#### Por Telegram
1. El paciente busca tu bot en Telegram
2. Envía `/start` o `/turno`
3. Same flujo que WhatsApp

### Para Administradores

#### Panel de Administración
1. Ve a: https://botodontologia.aiporvos.com/admin
2. Login con:
   - **Usuario**: admin
   - **Contraseña**: (la que configuraste en ADMIN_PASSWORD)

#### Funciones del Admin:
- **Pacientes**: Ver, agregar, editar, buscar
- **Profesionales**: Configurar doctores
- **Turnos**: Ver todos los turnos, filtrar por fecha
- **Registros Dentales**: Registrar tratamientos por diente
- **Consentimientos**: Ver aceptaciones de pacientes

#### Dashboard
1. Ve a: https://botodontologia.aiporvos.com/dashboard
2. Verás:
- Total de pacientes
- Turnos de hoy
- Turnos de la semana
- Pacientes nuevos del mes

---

## 🆕 Nuevas Funcionalidades Implementadas

### 🦷 Odontograma Digital Mejorado

El sistema ahora incluye un odontograma completo basado en fichas odontológicas estándar (OSPESYM):

#### Características:
- **Numeración FDI (ISO 3950)**: Sistema estándar internacional (18-11, 21-28, 31-38, 48-41)
- **Visualización de Arcadas**: Superior e inferior con orientación correcta
- **Marcado por Caras**: M (Mesial), D (Distal), O (Oclusal), V (Vestibular), P (Palatino)
- **Tabla de Tratamientos**: Registro completo tipo ficha odontológica
- **Códigos de Procedimientos**: Sistema de códigos estandarizados
- **Historial Visual**: Colores diferentes según el estado del tratamiento
- **Responsive**: Adaptable a dispositivos móviles y tablets

#### Acceso:
- URL: `/odontogram`
- O desde el menú lateral: "Odontograma"

#### Uso:
1. Buscar paciente en la barra superior
2. Seleccionar un diente haciendo clic
3. Completar el formulario con:
   - Caras afectadas
   - Tipo de tratamiento
   - Código del procedimiento
   - Profesional asignado
   - Costo
   - Observaciones
4. Guardar - el tratamiento aparece en la tabla y el diente cambia de color

---

### 📅 Sistema de Disponibilidad Real

Implementación completa de calendario propio en lugar de depender exclusivamente de Cal.com.

#### Ventajas:
- **Control Total**: Gestión interna de horarios sin dependencias externas
- **Turnos Variables**: Duraciones ajustables según el tipo de tratamiento
- **Sin Costos Externos**: Reduce dependencia de servicios de terceros
- **Integración Nativa**: Mejor experiencia con el bot conversacional
- **Privacidad**: Datos médicos permanecen en tu infraestructura

#### Configuración de Disponibilidad:
1. Ve a `/admin` → Profesionales → Selecciona un profesional
2. Configura los horarios de atención por día de la semana
3. Define duración de slots por defecto (generalmente 30 min)

#### Duraciones por Tipo de Tratamiento:
| Tratamiento | Duración | Profesional Sugerido |
|-------------|----------|---------------------|
| Consulta/Inicial | 15 min | Cualquiera |
| Limpieza | 15 min | General |
| Obturación | 30 min | General |
| Extracción | 30 min | Cirugía |
| Endodoncia | 60 min | Endodoncia |
| Corona | 45 min | Prótesis |
| Implante | 90 min | Implantología |
| Ortodoncia | 30 min | Ortodoncia |

#### Integración con Cal.com:
El sistema mantiene compatibilidad con Cal.com como **opción complementaria**:
- Los pacientes pueden reservar online si tienen acceso a Cal.com
- El webhook de Cal.com sincroniza los turnos con la base de datos
- La base de datos local es la **fuente de verdad principal**

---

### 🔔 Recordatorios Automáticos

Sistema automatizado de recordatorios de turnos.

#### Características:
- **Envío Automático**: Se ejecuta diariamente (configurable)
- **Multi-canal**: WhatsApp (Evolution API) y Email
- **Personalizado**: Incluye nombre del paciente, fecha, hora y profesional
- **Confirmación**: Los pacientes pueden confirmar o cancelar respondiendo

#### Configuración:

##### 1. Variables de Entorno Adicionales:
```env
# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-password-app
FROM_EMAIL=noreply@dentalstudio.com

# Recordatorios
REMINDER_DAYS_AHEAD=1  # Días de anticipación
REMINDER_SEND_TIME=09:00  # Hora de envío (formato 24h)
```

##### 2. Configurar Cron Job:

**Opción A - Cron Local:**
```bash
# Editar crontab
crontab -e

# Agregar línea (ejecuta todos los días a las 9 AM)
0 9 * * * cd /ruta/al/proyecto && python -m app.services.reminders
```

**Opción B - Docker:**
```bash
# Añadir al docker-compose.yml
services:
  reminders:
    image: botodontologia-app
    command: python -m app.services.reminders
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - EVOLUTION_URL=${EVOLUTION_URL}
    depends_on:
      - db
```

**Opción C - Ejecución Manual:**
```bash
python -m app.services.reminders
```

#### Mensaje de Recordatorio:
El sistema envía mensajes como:
```
👋 Hola [Nombre]!

📅 Te recordamos que tienes un turno agendado para mañana:

📆 Fecha: DD/MM/YYYY
⏰ Hora: HH:MM
🦷 Motivo: [Motivo]
👨‍⚕️ Profesional: [Nombre]

📍 Dirección: [Tu dirección]

Por favor confirma tu asistencia respondiendo:
✅ SI - Confirmo asistencia
❌ NO - Necesito cancelar/reprogramar

_Dental Studio Pro_ 🦷
```

---

## 📊 Arquitectura: Cal.com vs Calendario Propio

### Decisión Tomada: **Calendario Propio como Fuente de Verdad**

Después de analizar las necesidades del consultorio, se decidió implementar un **sistema híbrido**:

#### Calendario Propio (Principal):
- ✅ **Control total** sobre lógica de negocio
- ✅ **Turnos variables**: Duraciones personalizables según tratamiento
- ✅ **Sin dependencias externas**: Sin riesgo de downtime de terceros
- ✅ **Costo reducido**: Sin límites ni suscripciones
- ✅ **Integración perfecta** con el bot conversacional
- ✅ **Datos locales**: Privacidad y cumplimiento normativo

#### Cal.com (Complementario):
- ✅ **Reservas online**: Para pacientes que prefieren web
- ✅ **Integración existente**: Webhook funcional
- ⚠️ **Limitaciones**: Dependencia de servicio externo, costos en escala

#### Recomendación:
- Usar el **calendario propio** para todas las operaciones del bot
- Mantener **Cal.com** opcional para reservas web de pacientes
- Sincronizar mediante webhooks cuando sea necesario

---

## APIs Disponibles

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Página principal |
| GET | `/dashboard` | Dashboard con stats |
| GET | `/admin` | Panel de administración |
| GET | `/docs` | Documentación API |
| GET | `/odontogram` | Odontograma digital |
| GET | `/api/patients` | Lista de pacientes |
| GET | `/api/patients/search` | Buscar pacientes |
| GET | `/api/patients/{id}/treatments` | Tratamientos del paciente |
| GET | `/api/appointments/today` | Turnos de hoy |
| GET | `/api/appointments` | Lista de turnos |
| GET | `/api/stats` | Estadísticas |
| GET | `/api/professionals` | Lista de profesionales |
| GET | `/api/professionals/{id}/schedule` | Agenda del profesional |
| POST | `/api/availability/check` | Consultar disponibilidad |
| POST | `/api/treatments` | Crear tratamiento |
| POST | `/webhook` | Webhook de WhatsApp |
| POST | `/webhook/telegram` | Webhook de Telegram |
| POST | `/webhook/calcom` | Webhook de Cal.com |

### Autenticación

El admin usa autenticación básica. Agrega el header:
```
Authorization: Basic YWRtaW46YWRtaW4xMjM=
```
(donde `YWRtaW46YWRtaW4xMjM=` es `admin:password` en base64)

---

## Solución de Problemas

### El bot no responde

1. Verifica que el token de Telegram sea correcto
2. Revisa los logs: `docker-compose logs -f clinic-app`
3. Verifica que el webhook de Telegram esté configurado

### WhatsApp no conecta

1. Verifica que Evolution API esté corriendo
2. Revisa que el token de instancia sea correcto
3. El QR puede haber expirado → genera uno nuevo en la UI de Evolution

### No puedo acceder al admin

1. Verifica que las credenciales sean correctas
2. El usuario por defecto es: `admin`
3. La contraseña está en la variable `ADMIN_PASSWORD`

### Error de base de datos

1. Verifica que PostgreSQL esté corriendo
2. Revisa la variable `DATABASE_URL`
3. Asegúrate de que la DB exista

### Cambios no se reflejan

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Mantenimiento

### Backup de Base de Datos

```bash
docker exec clinic-db pg_dump -U clinic clinic > backup_$(date +%Y%m%d).sql
```

### Ver Logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo la app
docker-compose logs -f clinic-app

# Solo la DB
docker-compose logs -f postgres
```

### Actualizar la App

```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Estructura del Proyecto

```
clinic-app/
├── app/
│   ├── main.py           # FastAPI app
│   ├── bot.py            # Aiogram bot
│   ├── database.py       # SQLAlchemy config
│   ├── models.py         # Modelos de DB
│   ├── admin.py          # SQLAdmin setup
│   ├── handlers/
│   │   └── conversation.py  # Flujo de turnos
│   ├── services/
│   │   ├── cal_com.py    # Integración Cal.com
│   │   ├── evolution.py  # Integración WhatsApp
│   │   └── telegram.py   # Integración Telegram
│   └── utils/
│       ├── phone.py       # Utilidades de teléfono
│       └── classify.py   # Clasificador de motivos
├── templates/
│   └── dashboard.html    # Template del dashboard
├── static/               # Archivos estáticos
├── config.py            # Configuración
├── requirements.txt     # Dependencias Python
├── Dockerfile          # Imagen Docker
├── docker-compose.yml  # Orquestación
├── .env.example       # Ejemplo de variables
└── README.md          # Este archivo
```

---

## Próximos Pasos

1. ✅ Código creado
2. ⬜ Subir a Git
3. ⬜ Configurar en Dokploy
4. ⬜ Probar localmente
5. ⬜ Configurar webhooks
6. ⬜ Probar con pacientes

---

¿Necesitas ayuda con algún paso específico?
