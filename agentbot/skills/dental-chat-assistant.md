---
name: dental-chat-assistant
description: Maneja conversaciones de pacientes vía WhatsApp y Telegram para gestionar turnos odontológicos de forma automatizada.
---

# Dental Chat Assistant

Usa esta skill para construir un asistente conversacional que guía pacientes hasta confirmar turnos.

## Objetivo

Guiar al paciente paso a paso hasta confirmar un turno odontológico vía chat.

## Flujo conversacional

### Paso 1: Saludo y presentación

"Hola 👋 Soy el asistente virtual de Dental Studio Pro. Te ayudo a gestionar turnos de manera rápida y sencilla."

### Paso 2: Recolección de datos

```
pedir_datos_esenciales():
  - Nombre y apellido
  - DNI
  - Obra social (si tiene)
  - Teléfono
  - ¿Es paciente nuevo?
```

### Paso 3: Identificación del motivo

"¿Cuál es el motivo de tu consulta? Podés describirme con tus palabras."

### Paso 4: Clasificación automática

usar dental-intent-classifier para detectar:
- Tipo de consulta
- Profesional sugerido
- Prioridad

### Paso 5: Ofrecer opciones

"Perfecto 👌 Para [tipo_consulta] te puedo ofrecer estos turnos:"
- Turno 1
- Turno 2
- Turno 3

"Respondé con el número del turno que prefieras."

### Paso 6: Confirmación

"Confirmo tu turno:"
- Fecha y hora
- Profesional
- Motivo
- Dirección

"¿Confirmamos? (Sí/No)"

### Paso 7: Guardado

```
guardar_turno():
  - Crear paciente si no existe
  - Crear turno en sistema
  - Enviar confirmación
  - Agendar recordatorios
```

### Paso 8: Cierre

"¡Listo! Te esperamos. Te enviaremos un recordatorio antes del turno. ¿Necesitás algo más?"

## Reglas de UX

### Lenguaje

- Cordial y humano
- Frases cortas
- Emojis moderados
- Sin tecnicismos

### Gestión de errores

- Si paciente no entiende: reformular
- Si no hay turnos: ofrecer alternativas
- Si datos incompletos: pedir amablemente
- Si urgencia: priorizar

### Persistencia

- Guardar estado de conversación
- Permitir continuar más tarde
- Recordar contexto anterior

## Estados de conversación

- inicio: Recién comenzada
- recolectando_datos: Esperando info del paciente
- clasificando: Analizando motivo
- ofreciendo_turnos: Mostrando opciones
- confirmando: Esperando confirmación
- completada: Turno agendado
- escalada: Transferir a humano

## Integraciones

- dental-intent-classifier
- dental-scheduling (buscar disponibilidad)
- dental-admin-crud (crear paciente)
- dental-messaging-hub (registrar mensajes)
