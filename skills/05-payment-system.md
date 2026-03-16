# Skill: Sistema de Pagos y Cobros

## Descripción
Gestión completa de pagos, deudas, facturación y estado de cuenta de pacientes.

## Componentes

### 1. Registro de pagos
Campos:
- Paciente
- Monto
- Método de pago (efectivo, tarjeta, transferencia, etc.)
- Fecha
- Concepto/Descripción
- Número de comprobante (opcional)
- Profesional relacionado (opcional)

### 2. Deudas y saldos
- Generación automática de deuda al crear tratamiento
- Seguimiento de pagos parciales
- Cálculo de saldo pendiente
- Historial de pagos por paciente

### 3. Estados de cuenta
- Resumen mensual por paciente
- Detalle de tratamientos vs pagos
- Balance general de la clínica
- Reportes de ingresos

### 4. Métodos de pago soportados
- Efectivo
- Tarjeta de débito/crédito
- Transferencia bancaria
- Mercado Pago (integración opcional)
- Otros

## Flujo de trabajo

### Registrar un pago:
1. Buscar paciente
2. Verificar deudas pendientes
3. Ingresar monto y método
4. Asociar a tratamiento específico (opcional)
5. Guardar y generar comprobante

### Consultar estado de cuenta:
1. Seleccionar paciente
2. Ver tratamientos realizados
3. Ver pagos realizados
4. Calcular saldo

## API Endpoints
- GET /api/payments - Listar pagos
- POST /api/payments - Registrar pago
- GET /api/patients/{id}/payments - Pagos de paciente
- GET /api/patients/{id}/debts - Deudas de paciente
- GET /api/patients/{id}/account - Estado de cuenta completo

## Reportes financieros
- Ingresos diarios/semanales/mensuales
- Pagos por método
- Deudas pendientes
- Profesionales con más ingresos
- Comparativos período vs período

## Integraciones opcionales
- Mercado Pago (botón de pago)
- Facturación electrónica (AFIP Argentina)
- Sincronización con contabilidad

## Consideraciones
- Registrar siempre el método de pago
- Guardar comprobantes escaneados (opcional)
- Permitir pagos parciales
- Manejar devoluciones/reembolsos
- Auditar cambios en pagos
