---
name: dental-security-audit
description: Define permisos, trazabilidad y auditoría para un sistema odontológico administrativo con información sensible y operaciones críticas.
---

# Dental Security Audit

Usa esta skill cuando debas definir seguridad funcional y controles de acceso.

## Objetivo

Diseñar una base seria de permisos y auditoría.

## Roles sugeridos

- super_admin
- admin_clinica
- recepcion
- profesional
- caja
- soporte

## Recursos mínimos

- pacientes
- profesionales
- agenda
- tratamientos
- historia_clinica
- pagos
- mensajes
- reportes
- configuracion
- usuarios
- auditoria

## Acciones

- view
- create
- edit
- delete
- assign
- export
- confirm
- cancel
- reschedule
- send
- manage

## Reglas

- Historia clínica y pagos requieren trazabilidad
- Toda acción sensible debe quedar auditada
- Registrar quién hizo qué, cuándo y desde dónde si aplica
- Ocultar acciones no permitidas en UI
- Validar permisos también en backend

## Auditoría mínima

- usuario
- acción
- entidad
- id_entidad
- timestamp
- cambios relevantes
- origen o contexto

## Respuesta esperada

- matriz de permisos
- política RBAC
- eventos auditables
- recomendaciones backend/frontend
