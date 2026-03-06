# Modelos de Base de Datos

El proyecto usa SQLAlchemy ORM con PostgreSQL.

## Esquema

### Patient (Pacientes)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| first_name | String(100) | Nombre |
| last_name | String(100) | Apellido |
| dni | String(20) | DNI |
| obra_social | String(100) | Obra social |
| phone | String(20) | Teléfono |
| email | String(100) | Email |
| notes | Text | Notas |
| created_at | DateTime | Fecha creación |
| updated_at | DateTime | Fecha actualización |

**Relaciones:**
- appointments (1:N)
- dental_records (1:N)
- dental_treatments (1:N)
- payments (1:N)
- debts (1:N)
- consents (1:N)

---

### Professional (Profesionales)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| full_name | String(200) | Nombre completo |
| specialty | String(100) | Especialidad |
| location | String(200) | Ubicación |
| is_active | Boolean | Activo |
| created_at | DateTime | Fecha creación |

**Relaciones:**
- appointments (1:N)
- availabilities (1:N)
- dental_treatments (1:N)

---

### Appointment (Turnos)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| patient_id | Integer | FK Patient |
| professional_id | Integer | FK Professional |
| start_at | DateTime | Inicio |
| end_at | DateTime | Fin |
| reason | String(200) | Motivo |
| status | String(20) | Estado |
| category | String(50) | Categoría |
| notes | Text | Notas |
| created_at | DateTime | Fecha creación |

**Estados:** `scheduled`, `confirmed`, `completed`, `cancelled`, `no_show`

---

### Availability (Disponibilidad)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| professional_id | Integer | FK Professional |
| day_of_week | Integer | Día (0=Lunes, 6=Domingo) |
| start_time | Time | Hora inicio |
| end_time | Time | Hora fin |
| is_active | Boolean | Activo |

---

### DentalRecord (Registros Dentales)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| patient_id | Integer | FK Patient |
| record_date | Date | Fecha |
| record_status | String(20) | Estado |
| notes | Text | Notas |
| created_at | DateTime | Fecha creación |

---

### DentalTreatment (Tratamientos Dentales)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| patient_id | Integer | FK Patient |
| professional_id | Integer | FK Professional |
| tooth | String(10) | Diente |
| face | String(10) | Cara |
| treatment_name | String(200) | Nombre |
| treatment_code | String(20) | Código |
| treatment_price_id | Integer | FK TreatmentPrice |
| status | String(20) | Estado |
| treatment_date | Date | Fecha |
| cost | Integer | Costo |
| notes | Text | Notas |

---

### TreatmentPrice (Precios)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| code | String(20) | Código |
| name | String(200) | Nombre |
| description | Text | Descripción |
| price | Integer | Precio |
| is_active | Boolean | Activo |
| created_at | DateTime | Fecha creación |

---

### Payment (Pagos)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| patient_id | Integer | FK Patient |
| amount | Integer | Monto |
| payment_method | String(20) | Método |
| payment_date | DateTime | Fecha |
| reference | String(100) | Referencia |
| notes | Text | Notas |

**Métodos:** `cash`, `card`, `transfer`, `mercadopago`

---

### Debt (Deudas)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| patient_id | Integer | FK Patient |
| description | String(200) | Descripción |
| amount | Integer | Monto |
| status | String(20) | Estado |
| due_date | Date | Fecha vencimiento |
| notes | Text | Notas |
| created_at | DateTime | Fecha creación |

**Estados:** `pending`, `paid`, `overdue`

---

### Consent (Consentimientos)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| patient_id | Integer | FK Patient |
| consent_type | String(50) | Tipo |
| accepted | Boolean | Aceptado |
| signed_at | DateTime | Fecha firma |
| notes | Text | Notas |

---

### ChatSession (Sesiones de Chat)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| patient_id | Integer | FK Patient |
| channel | String(20) | Canal |
| step | String(20) | Paso |
| data | JSON | Datos |
| created_at | DateTime | Fecha creación |
| updated_at | DateTime | Fecha actualización |

**Canales:** `telegram`, `whatsapp`

---

### AdminUser (Usuarios Admin)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| username | String(50) | Usuario (único) |
| password_hash | String(200) | Hash contraseña |
| is_active | Boolean | Activo |
| created_at | DateTime | Fecha creación |

---

## Inicialización

Las tablas se crean automáticamente al iniciar la app:

```python
# app/database.py
def init_db():
    Base.metadata.create_all(bind=engine)
```

---

## Relaciones UML

```
Patient 1 -- * Appointment
Patient 1 -- * DentalRecord
Patient 1 -- * DentalTreatment
Patient 1 -- * Payment
Patient 1 -- * Debt
Patient 1 -- * Consent
Patient 1 -- * ChatSession

Professional 1 -- * Appointment
Professional 1 -- * Availability
Professional 1 -- * DentalTreatment
```
