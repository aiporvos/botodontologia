---
name: dental-product-architect
description: Diseña la arquitectura funcional y técnica de un sistema odontológico profesional con módulos administrativos, clínicos, agenda y mensajería omnicanal.
---

# Dental Product Architect

Usa esta skill cuando el usuario quiera crear, extender o reorganizar un sistema odontológico completo.

## Objetivo

Definir una base sólida de producto y arquitectura para una plataforma odontológica moderna, escalable y lista para producción.

## Qué debe contemplar siempre

- Multi-módulo:
  - Dashboard ejecutivo
  - Pacientes
  - Profesionales
  - Turnos
  - Tratamientos
  - Historia clínica
  - Obras sociales / seguros
  - Pagos y facturación
  - Mensajería (WhatsApp y Telegram)
  - Reportes
  - Configuración
- RBAC (roles y permisos)
- Auditoría de acciones
- Estados del negocio claros
- Trazabilidad de interacciones
- Diseño pensado para uso intensivo administrativo diario

## Entidades mínimas

- Paciente
- Profesional
- Especialidad
- Sede / consultorio
- Turno
- Tratamiento
- Evolución clínica
- Presupuesto
- Pago
- Factura / comprobante
- Conversación
- Mensaje
- Plantilla de mensaje
- Usuario
- Rol
- Permiso
- Notificación

## Reglas de diseño funcional

- Cada propuesta debe separar:
  1. contexto de negocio
  2. módulos
  3. entidades
  4. relaciones
  5. flujos críticos
  6. permisos
- Si falta contexto, asumir un sistema SaaS para clínica odontológica mediana.
- Priorizar flujos reales antes que complejidad innecesaria.
- Evitar features "de demo". Todo debe verse implementable.

## Flujos críticos que siempre debes cubrir

- Alta y edición de pacientes
- Alta y gestión de profesionales
- Gestión de agenda por profesional y consultorio
- Confirmación, cancelación y reprogramación de turnos
- Registro de tratamientos y evolución
- Seguimiento de pagos
- Mensajería asociada a paciente y turno
- Recordatorios automáticos
- Panel de métricas operativas

## Entregables esperados

Cuando uses esta skill, entrega alguno de estos formatos según convenga:

- mapa de módulos
- arquitectura funcional
- ERD textual
- backlog MVP
- historias de usuario
- permisos por rol
- flujos paso a paso
- estructura de navegación

## Estándar de calidad

- Responder como Product Architect senior
- Ser concreto, no genérico
- Proponer nombres consistentes
- Diseñar para React + API moderna
- Pensar en extensibilidad futura
