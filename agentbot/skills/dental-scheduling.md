---
name: dental-scheduling
description: Diseña e implementa agenda, calendario y gestión de turnos para clínicas odontológicas con foco en disponibilidad, confirmación y reprogramación.
---

# Dental Scheduling

Usa esta skill para todo lo relacionado con turnos, calendario, disponibilidad y operaciones de agenda.

## Objetivo

Crear una experiencia de agenda sólida para clínica odontológica.

## Casos de uso mínimos

- Crear turno
- Confirmar turno
- Cancelar turno
- Reprogramar turno
- Marcar asistencia
- Marcar ausencia
- Ver agenda por día / semana
- Ver agenda por profesional
- Ver disponibilidad
- Bloquear horarios
- Registrar motivo de cancelación

## Reglas de negocio

- Un turno pertenece a paciente, profesional y consultorio/sede
- Debe existir estado claro del turno
- Debe quedar historial de cambios
- Evitar dobles reservas
- Permitir buffers entre turnos si el negocio lo pide
- Permitir observaciones administrativas y clínicas separadas

## Estados sugeridos

- pendiente
- confirmado
- cancelado
- reprogramado
- asistió
- no_asistió
- en_espera

## UI obligatoria

- vista calendario
- vista lista
- filtros por profesional, fecha, sede y estado
- badge de estado
- panel lateral o modal de detalle
- acciones rápidas
- indicadores visuales muy claros

## Integraciones esperables

- recordatorios automáticos
- link con mensajería
- link con ficha del paciente
- link con tratamiento o motivo de consulta

## Respuesta esperada

- modelo de turno
- reglas de negocio
- estados
- componentes React
- endpoints sugeridos
- validaciones
- flujos UX
