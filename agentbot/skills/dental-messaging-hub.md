---
name: dental-messaging-hub
description: Diseña e implementa una bandeja omnicanal profesional para WhatsApp y Telegram integrada al sistema odontológico con pacientes, turnos y automatizaciones.
---

# Dental Messaging Hub

Usa esta skill para construir el módulo de mensajería centralizado.

## Objetivo

Crear una bandeja de conversaciones profesional, usable y bien integrada al negocio odontológico.

## Canales

- WhatsApp
- Telegram

## Principios

- Una conversación puede vincularse a un paciente
- Una conversación puede vincularse a uno o más turnos
- Debe verse el canal claramente
- Debe existir historial completo
- Debe haber etiquetas y estados
- Debe permitir atención manual y automatizada

## Funcionalidades mínimas

- Inbox unificada
- Filtro por canal
- Filtro por estado
- Filtro por profesional o sede
- Asignación de conversación
- Etiquetas
- Plantillas rápidas
- Respuestas predefinidas
- Vista de hilo
- Datos del paciente en sidebar
- Turnos relacionados
- Recordatorios y confirmaciones
- Registro de último contacto

## Estados sugeridos

- nuevo
- pendiente
- en_gestion
- respondido
- cerrado

## Diseño de pantalla

### Columna 1

- filtros
- bandeja
- contadores

### Columna 2

- conversación activa
- mensajes
- input de respuesta
- plantillas
- adjuntos si aplica

### Columna 3

- ficha resumida del paciente
- próximos turnos
- historial reciente
- tags
- acciones rápidas

## Reglas UX

- Priorizar velocidad operativa
- El canal debe identificarse de inmediato
- Mensajes entrantes y salientes bien diferenciados
- Poder responder sin perder contexto del paciente
- Evitar saturación visual

## Entregables esperados

- arquitectura del módulo
- modelo Conversación/Mensaje
- layout de inbox
- componentes React
- estados y badges
- eventos clave
- automatizaciones sugeridas
