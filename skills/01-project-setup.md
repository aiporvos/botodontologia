# Skill: Configuración Inicial del Proyecto Dental Studio Pro

## Descripción
Configurar el entorno de desarrollo y producción para el sistema de gestión odontológica.

## Prerrequisitos
- Acceso al repositorio GitHub
- Base de datos PostgreSQL disponible
- Variables de entorno configuradas

## Pasos

### 1. Clonar y configurar el repositorio
```bash
git clone https://github.com/aiporvos/botodontologia.git
cd botodontologia
```

### 2. Configurar variables de entorno
Crear archivo `.env` con:
- TELEGRAM_BOT_TOKEN
- DATABASE_URL (PostgreSQL)
- OPENAI_API_KEY
- CALCOM_API_KEY (opcional)

### 3. Instalar dependencias
Instalar todas las dependencias listadas en requirements.txt

### 4. Inicializar la base de datos
- Ejecutar migraciones automáticas
- Crear usuario admin por defecto
- Crear profesionales por defecto (Dr. Silvestro, Dra. Murad)
- Configurar disponibilidad horaria de profesionales

### 5. Verificar instalación
- Acceder a http://localhost:8000
- Login con admin/admin123
- Verificar que todas las páginas carguen correctamente

## Consideraciones importantes
- El sistema requiere PostgreSQL (no SQLite para producción)
- Configurar correctamente los horarios de disponibilidad de profesionales
- El bot de Telegram debe estar configurado con Webhook o Polling
- Cal.com integration opcional pero recomendada

## Verificación
- [ ] Login funciona
- [ ] Dashboard carga estadísticas
- [ ] Agenda muestra calendario
- [ ] Pacientes se listan
- [ ] Odontograma funciona
