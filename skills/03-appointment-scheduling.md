# Skill: Gestión de Turnos y Agenda

## Descripción
Sistema completo de gestión de turnos con calendario, disponibilidad y notificaciones.

## Componentes principales

### 1. Calendario
- Vista mensual, semanal y diaria
- Drag & drop para mover turnos
- Colores según tipo de tratamiento
- Indicadores de estado (confirmado, pendiente, cancelado)

### 2. Creación de turnos
- Seleccionar paciente (búsqueda en tiempo real)
- Seleccionar profesional
- Seleccionar fecha y hora
- Definir duración según tratamiento
- Motivo de la consulta
- Notas adicionales

### 3. Tipos de tratamiento y duraciones
- Consulta general: 15 min
- Limpieza: 15 min
- Extracción: 30 min
- Endodoncia/Conducto: 60 min
- Ortodoncia: 30 min
- Corona: 45 min
- Implante: 90 min
- Prótesis: 30 min

### 4. Profesionales y especialidades
- Dr. Silvestro: Extracciones, Implantes, Prótesis
- Dra. Murad: Ortodoncia, Endodoncia
- Asignación automática según tratamiento

### 5. Disponibilidad
Configurar horarios de atención por profesional:
- Días de la semana
- Hora de inicio y fin
- Slot de duración (default 30 min)

### 6. Estados de turno
- confirmed: Turno confirmado
- pending: Pendiente de confirmación
- cancelled: Cancelado
- completed: Atendido

### 7. Notificaciones
- Recordatorios automáticos (24h y 2h antes)
- Confirmación vía WhatsApp/Telegram
- Cancelaciones

## API Endpoints
- GET /api/appointments - Listar turnos
- POST /api/appointments - Crear turno
- GET /api/appointments/today - Turnos de hoy
- PUT /api/appointments/{id} - Actualizar turno
- DELETE /api/appointments/{id} - Cancelar turno
- GET /api/appointments?start={}&end={} - Turnos por rango

## Integración con Cal.com (opcional)
- Sincronización bidireccional
- Webhooks para nuevos turnos
- Actualización en tiempo real

## Consideraciones importantes
- Validar que no haya solapamiento de turnos
- Verificar disponibilidad del profesional
- Enviar confirmación al paciente
- Manejar zonas horarias correctamente
