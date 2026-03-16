# Skill: Configuración del Bot de Telegram/WhatsApp

## Descripción
Configurar y personalizar el bot conversacional para atención al paciente 24/7.

## Funcionalidades del Bot

### 1. Consulta de disponibilidad
- Paciente escribe su necesidad (ej: "tengo dolor de muela")
- Bot identifica tipo de tratamiento
- Busca horarios disponibles
- Presenta opciones con profesional asignado

### 2. Agendamiento de turnos
- Recolecta datos del paciente:
  - Nombre completo
  - DNI
  - Teléfono
  - Obra social
- Confirma horario elegido
- Guarda turno en sistema
- Envía confirmación

### 3. Recordatorios automáticos
- 24 horas antes del turno
- 2 horas antes del turno
- Confirmación de asistencia
- Reagendamiento si es necesario

### 4. Consulta de información
- Precios de tratamientos
- Ubicación del consultorio
- Horarios de atención
- Obras sociales aceptadas

### 5. Cancelaciones
- Permite cancelar turno
- Motivo de cancelación (opcional)
- Liberar slot en agenda

## Configuración

### Telegram Bot
1. Crear bot con @BotFather
2. Obtener token
3. Configurar webhook o polling
4. Establecer comandos:
   - /start - Iniciar conversación
   - /turno - Agendar turno
   - /precios - Ver precios
   - /ayuda - Ayuda

### WhatsApp (Evolution API)
1. Configurar Evolution API
2. Crear instancia
3. Conectar número de WhatsApp
4. Configurar webhook
5. Definir palabras clave de inicio

## Personalización del AI

### Prompt del sistema
Definir:
- Personalidad del bot (amable, profesional, eficiente)
- Reglas de negocio
- Escalación a humano
- Limitaciones

### Herramientas disponibles
- ConsultarPrecios
- ConsultarDisponibilidad
- AgendarTurno
- GestionarContactos
- EnviarEmail

### Flujo conversacional
1. Saludo y bienvenida
2. Identificar necesidad
3. Ofrecer soluciones
4. Recolectar datos
5. Confirmar acción
6. Seguimiento

## Monitoreo
- Logs de conversaciones
- Métricas de uso
- Tasa de conversión (consulta → turno)
- Satisfacción del usuario
- Errores y fallos

## Consideraciones
- Responder siempre en español
- Usar lenguaje claro y simple
- No inventar información
- Escalar a humano cuando sea necesario
- Manejar errores gracefully
- Respetar horarios de atención

## Fallbacks
- Si no entiende: "¿Podrías reformular tu pregunta?"
- Si no hay disponibilidad: "Te sugiero llamar al consultorio"
- Si es emergencia: "Por favor dirígete a guardia o llama al..."

## Seguridad
- No pedir datos sensibles por chat
- Validar identidad antes de acciones importantes
- Logs de auditoría de todas las acciones
