---
name: dental-admin-crud
description: Implementa módulos CRUD robustos para pacientes, profesionales, tratamientos, pagos y configuraciones de un sistema odontológico administrativo.
---

# Dental Admin CRUD

Usa esta skill cuando haya que construir módulos de gestión administrativa completos.

## Objetivo

Crear CRUDs profesionales, consistentes y listos para producción.

## Módulos típicos

- Pacientes
- Profesionales
- Especialidades
- Sedes / consultorios
- Obras sociales
- Tratamientos
- Presupuestos
- Pagos
- Plantillas de mensaje
- Usuarios y roles

## Patrón obligatorio para cada módulo

Cada módulo debe incluir:

- listado
- búsqueda
- filtros
- ordenamiento
- paginación
- vista detalle
- alta
- edición
- baja lógica si aplica
- validaciones
- feedback visual
- permisos por acción
- historial o auditoría si es crítico

## Tabla estándar

Toda tabla debe considerar:

- columnas útiles
- filtros rápidos
- acciones por fila
- selección múltiple si aporta valor
- estado visual claro
- exportación si tiene sentido

## Formularios

- Validación del lado cliente y servidor
- Campos agrupados por lógica de negocio
- Labels claros
- Inputs accesibles
- Mensajes de error accionables
- Modo crear y editar reutilizable

## Convenciones

- Nombres de componentes predecibles
- Separar container, hooks, services y presentational components
- Evitar duplicar lógica
- Mantener tipos bien definidos
- Pensar siempre en mantenimiento futuro

## Salida esperada

Cuando uses esta skill, devolver:

- estructura de archivos
- modelo de datos del módulo
- componentes
- hooks
- servicios
- tipos
- pantalla de listado
- pantalla de detalle
- formulario
- validaciones
