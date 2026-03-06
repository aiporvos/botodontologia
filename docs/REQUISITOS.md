# Requisitos del Proyecto - Clínica Dental

## 1. Requisitos Funcionales

### 1.1 Gestión de Pacientes
- [x] Registrar pacientes con: nombre, apellido, DNI, teléfono, obra social, email
- [x] Buscar pacientes por nombre, DNI o teléfono
- [x] Editar información de pacientes
- [x] Ver historial de tratamientos por paciente
- [x] Notas por paciente

### 1.2 Gestión de Turnos
- [x] Solicitar turno por WhatsApp
- [x] Solicitar turno por Telegram
- [x] Flujo de conversación para agendar turno
- [x] Confirmación de turno
- [x] Cancelación de turno
- [x] Ver turnos del día
- [x] Ver turnos de la semana

### 1.3 Gestión de Profesionales
- [x] Registro de profesionales/dentistas
- [x] Especialidad del profesional
- [x] Disponibilidad por día y horario

### 1.4 Registros Dentales
- [x] Odontograma (mapa de dientes)
- [x] Registrar tratamientos por diente
- [x] Registro de estado dental por paciente

### 1.5 Gestión Financiera
- [x] Registro de pagos
- [x] Control de deudas
- [x] Lista de precios de tratamientos

### 1.6 Consentimientos
- [x] Registro de consentimientos firmados
- [x] Tipos de consentimiento

---

## 2. Requisitos Técnicos

### 2.1 Integraciones
- [x] Bot de Telegram para atención
- [x] Bot de WhatsApp para atención
- [x] Integración con sistema de reservas externo
- [ ] Integración completa con WhatsApp (webhooks)

### 2.2 Panel de Administración
- [x] Interfaz web para gestión
- [x] CRUD de pacientes
- [x] CRUD de profesionales
- [x] CRUD de turnos
- [x] Ver registros dentales
- [x] Ver/administrar pagos y deudas

### 2.3 API
- [x] Endpoints REST para pacientes
- [x] Endpoints para turnos
- [x] Endpoints para tratamientos
- [x] Endpoints para pagos
- [x] Endpoints para deudas
- [x] Webhook para WhatsApp
- [x] Webhook para Telegram

### 2.4 Dashboard
- [x] Estadísticas de pacientes
- [x] Turnos de hoy
- [x] Turnos de la semana
- [x] Pacientes nuevos del mes

---

## 3. Estado de Implementación

| Módulo | Estado | Observaciones |
|--------|--------|---------------|
| Pacientes | ✅ Completo | CRUD completo |
| Turnos | ✅ Completo | Bot conversacional implementado |
| Profesionales | ✅ Completo | Especialidades configurables |
| Disponibilidad | ✅ Completo | Días y horarios |
| Registros Dentales | ✅ Parcial | Estructura creada, UI básica |
| Tratamientos | ✅ Completo | Por diente y cara |
| Pagos | ✅ Completo | Métodos: efectivo, tarjeta, transferencia |
| Deudas | ✅ Completo | Seguimiento de pendientes |
| Consentimientos | ✅ Parcial | Estructura creada |
| Dashboard | ✅ Completo | Estadísticas generales |
| WhatsApp | 🔶 Parcial | Webhook configurado, flujo parcial |
| Telegram | 🔶 Parcial | Bot configurado, no conectado |

---

## 4. Pendiente de Completar

### 4.1 WhatsApp
- [ ] Conectar webhook de Evolution API correctamente
- [ ] Probar flujo completo de solicitud de turno por WhatsApp
- [ ] Configurar QR de instancia

### 4.2 Telegram
- [ ] Conectar bot con webhook
- [ ] Probar flujo completo

### 4.3 Integración con Cal.com
- [ ] Sincronizar turnos con calendario externo
- [ ] Mostrar disponibilidad desde sistema externo

### 4.4 Funcionalidades Adicionales
- [ ] Recordatorios de turnos (notificaciones)
- [ ] Confirmación de turno por email/SMS
- [ ] Reportes PDF de tratamientos
- [ ] Estadísticas avanzadas
- [ ] Login de usuarios pacientes

### 4.5 UI/UX
- [ ] Mejorar diseño del dashboard
- [ ] Página de odontograma interactiva completa
- [ ] Formularios de contacto

---

## 5. Servicios Externos Requeridos

| Servicio | Estado | Acción Requerida |
|---------|--------|-----------------|
| Telegram Bot | 🔶 Parcial | Conectar token y webhook |
| WhatsApp (Evolution) | 🔶 Parcial | Configurar instancia y webhook |
| Cal.com | 🔶 Parcial | Conectar API key |
| Base de Datos | ✅ Listo | PostgreSQL funcionando |

---

## 6. Pasos para Completar

### Paso 1: Conectar Telegram
1. Obtener token de @BotFather
2. Configurar webhook: `https://tu-dominio.com/webhook/telegram`
3. Probar con /start

### Paso 2: Conectar WhatsApp
1. Crear instancia en Evolution API
2. Escanear QR
3. Configurar webhook: `https://tu-dominio.com/webhook`
4. Probar flujo completo

### Paso 3: Conectar Cal.com
1. Obtener API key
2. Configurar variables de entorno
3. Sincronizar disponibilidad

### Paso 4: Pruebas
1. Probar flujo completo paciente
2. Verificar registros en admin
3. Probar cancelaciones

---

## 7. Estructura de Datos Activa

```
Paciente
├── Turnos (muchos)
├── Registros Dentales (muchos)
├── Tratamientos (muchos)
├── Pagos (muchos)
├── Deudas (muchos)
└── Consentimientos (muchos)

Profesional
├── Turnos (muchos)
├── Disponibilidades (muchos)
└── Tratamientos (muchos)
```

---

## 8. Notas Técnicas

- La aplicación usa un flujo de conversación por pasos
- Cada chat tiene una sesión con estado (step)
- Los datos se almacenan en PostgreSQL
- El panel admin usa interfaz visual
- Las tablas se crean automáticamente al iniciar
