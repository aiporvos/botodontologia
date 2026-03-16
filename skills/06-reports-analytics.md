# Skill: Reportes y Analytics

## Descripción
Generación de reportes estadísticos y análisis de datos para toma de decisiones.

## Tipos de reportes

### 1. Reportes de pacientes
- Total de pacientes activos
- Nuevos pacientes por período
- Pacientes por obra social
- Pacientes recurrentes vs nuevos
- Edad promedio y demografía

### 2. Reportes de turnos
- Turnos por día/semana/mes
- Tasa de asistencia/cancelación
- Turnos por profesional
- Tratamientos más solicitados
- Horarios pico de demanda

### 3. Reportes financieros
- Ingresos totales por período
- Ingresos por profesional
- Deudas pendientes
- Pagos por método
- Comparativa año vs año

### 4. Reportes de odontograma
- Tratamientos más frecuentes
- Caries por cuadrante
- Tratamientos pendientes
- Historial por tipo de procedimiento

### 5. Reportes operativos
- Ocupación de agenda
- Tiempo promedio de espera
- Duración real vs estimada de turnos
- Profesional más solicitado

## Filtros disponibles
- Rango de fechas
- Profesional específico
- Tipo de tratamiento
- Estado de turno
- Obra social
- Canal de llegada (web, bot, presencial)

## Exportación
- PDF para presentación
- Excel para análisis
- CSV para integración
- Email automático periódico

## Dashboard en tiempo real
- KPIs principales
- Gráficos interactivos
- Comparativas
- Alertas (ej: profesional con baja ocupación)

## API Endpoints
- GET /api/stats - Estadísticas generales
- GET /api/reports/patients - Reporte de pacientes
- GET /api/reports/appointments - Reporte de turnos
- GET /api/reports/financial - Reporte financiero
- GET /api/reports/treatments - Reporte de tratamientos

## Automatización
- Envío automático de reportes semanales
- Alertas por email cuando se alcanzan umbrales
- Backup automático de datos

## Privacidad
- No incluir datos personales identificables en reportes agregados
- Cumplimiento con regulaciones de protección de datos
- Acceso restringido según rol de usuario
