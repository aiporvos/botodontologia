# Skill: Gestión de Pacientes

## Descripción
Administrar el catálogo de pacientes, altas, bajas, modificaciones y búsquedas.

## Funcionalidades

### 1. Alta de pacientes
Campos requeridos:
- Nombre y Apellido
- DNI (opcional pero recomendado)
- Teléfono (obligatorio)
- Email (opcional)
- Obra Social / Prepaga
- Dirección (opcional)
- Notas adicionales

### 2. Búsqueda de pacientes
- Búsqueda por nombre, apellido, DNI o teléfono
- Filtros por obra social
- Historial de búsquedas recientes

### 3. Edición de pacientes
- Actualización de datos personales
- Cambio de obra social
- Actualización de contacto

### 4. Historial del paciente
- Ver turnos anteriores
- Ver tratamientos realizados
- Ver estado de cuenta (pagos/deudas)
- Ver odontograma completo

### 5. Importación/Exportación
- Exportar lista de pacientes a CSV/Excel
- Importar pacientes desde archivo

## API Endpoints relevantes
- GET /api/patients - Listar pacientes
- POST /api/patients - Crear paciente
- GET /api/patients/{id} - Obtener paciente
- PUT /api/patients/{id} - Actualizar paciente
- DELETE /api/patients/{id} - Eliminar paciente
- GET /api/patients/search?q={query} - Buscar pacientes

## Consideraciones
- El DNI debe ser único
- El teléfono es el identificador principal para el bot
- Mantener historial de modificaciones
- No eliminar pacientes con turnos o tratamientos (solo desactivar)
