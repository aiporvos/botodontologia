# API REST

La aplicación expone una API REST para interactuar con los datos.

## URLs Base

- **Local**: http://localhost:8000
- **Producción**: http://tu-dominio.com

## Documentación Interactiva

http://tu-dominio.com/docs

---

## Endpoints

### Pacientes

#### GET /api/patients
Lista todos los pacientes.

```bash
curl http://localhost:8000/api/patients
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Juan Pérez",
    "phone": "+5491112345678",
    "obra_social": "OSDE",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

#### GET /api/patients/search?q=busqueda
Buscar pacientes por nombre, DNI o teléfono.

```bash
curl "http://localhost:8000/api/patients/search?q=juan"
```

#### POST /api/patients
Crear nuevo paciente.

```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan",
    "last_name": "Pérez",
    "dni": "12345678",
    "phone": "+5491112345678",
    "obra_social": "OSDE"
  }'
```

---

### Turnos

#### GET /api/appointments/today
Turnos del día actual.

```bash
curl http://localhost:8000/api/appointments/today
```

---

### Tratamientos

#### GET /api/patients/{id}/treatments
Tratamientos de un paciente.

```bash
curl http://localhost:8000/api/patients/1/treatments
```

#### POST /api/treatments
Crear tratamiento.

```bash
curl -X POST http://localhost:8000/api/treatments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "tooth": "11",
    "face": "O",
    "treatment_name": "Limpieza",
    "treatment_type": "L",
    "cost": 5000,
    "treatment_date": "2024-01-15"
  }'
```

---

### Pagos

#### GET /api/payments
Lista todos los pagos.

```bash
curl http://localhost:8000/api/payments
```

#### POST /api/payments
Crear pago.

```bash
curl -X POST http://localhost:8000/api/payments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "amount": 5000,
    "payment_method": "cash",
    "reference": "recibo-001"
  }'
```

---

### Deudas

#### GET /api/debts
Lista todas las deudas.

```bash
curl http://localhost:8000/api/debts
```

#### POST /api/debts
Crear deuda.

```bash
curl -X POST http://localhost:8000/api/debts \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "description": "Tratamiento pendiente",
    "amount": 10000,
    "due_date": "2024-02-15"
  }'
```

#### POST /api/debts/{id}/pay
Marcar deuda como pagada.

```bash
curl -X POST http://localhost:8000/api/debts/1/pay
```

---

### Estadísticas

#### GET /api/stats
Estadísticas generales.

```bash
curl http://localhost:8000/api/stats
```

**Response:**
```json
{
  "patients": 150,
  "appointments": 320,
  "professionals": 3
}
```

---

### Webhooks

#### POST /webhook
Webhook para Evolution API (WhatsApp).

```
POST http://tu-dominio.com/webhook
```

#### POST /webhook/telegram
Webhook para Telegram.

```
POST http://tu-dominio.com/webhook/telegram
```

---

## Páginas Web

| Ruta | Descripción |
|------|-------------|
| `/` | Página principal |
| `/admin` | Panel de administración |
| `/dashboard` | Dashboard con estadísticas |
| `/odontogram` | Odontograma interactivo |
| `/payments` | Gestión de cobros |
| `/docs` | Documentación API (Swagger) |
