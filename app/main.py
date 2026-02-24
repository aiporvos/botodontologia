from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from app.database import engine, init_db
from app.admin import setup_admin
from app.handlers.conversation import handle_whatsapp_message
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Patient, Appointment, Professional
from datetime import datetime, timedelta


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización al iniciar la app"""
    # Inicializar base de datos
    print("📦 Inicializando base de datos...")
    init_db()

    # Crear admin por defecto si no existe
    from app.models import AdminUser

    db = SessionLocal()
    try:
        admin = (
            db.query(AdminUser)
            .filter(AdminUser.username == settings.admin_username)
            .first()
        )
        if not admin:
            import hashlib

            password_hash = hashlib.sha256(settings.admin_password.encode()).hexdigest()
            admin = AdminUser(
                username=settings.admin_username, password_hash=password_hash
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin creado: {settings.admin_username}")
    finally:
        db.close()

    # Crear profesionales por defecto si no existen
    db = SessionLocal()
    try:
        prof_count = db.query(Professional).count()
        if prof_count == 0:
            professionals = [
                Professional(
                    full_name="Dr. Silvestro",
                    specialty="extracciones/implantes/protesis",
                ),
                Professional(full_name="Dra. Murad", specialty="ortodoncia/conductos"),
            ]
            for prof in professionals:
                db.add(prof)
            db.commit()
            print("✅ Profesionales por defecto creados")
    finally:
        db.close()

    print("🚀 App iniciada correctamente")
    yield
    print("👋 App cerrada")


# Crear app FastAPI
app = FastAPI(
    title="Clínica Dental API",
    description="API para gestión de clínica odontológica",
    version="1.0.0",
    lifespan=lifespan,
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Configurar SQLAdmin
setup_admin(app, engine)

# Importar después de crear app para evitar ciclos
from sqlalchemy.orm import Session as SessionLocal


# ==================== RUTAS ====================


@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal"""
    return """
    <html>
        <head>
            <title>Clínica Dental</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                h1 { color: #2c3e50; }
                .links { margin-top: 20px; }
                .links a { display: block; margin: 10px 0; color: #3498db; text-decoration: none; }
                .links a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🦷 Clínica Dental API</h1>
                <p>Sistema de gestión de turnos odontológicos</p>
                <div class="links">
                    <a href="/admin">📊 Panel de Administración</a>
                    <a href="/docs">📚 Documentación API</a>
                    <a href="/dashboard">📈 Dashboard</a>
                    <a href="/odontogram">🦷 Odontograma</a>
                    <a href="/payments">💰 Cobros</a>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(db: Session = Depends(get_db)):
    """Dashboard con estadísticas"""
    from sqlalchemy import func

    # Estadísticas
    total_patients = db.query(func.count(Patient.id)).scalar() or 0
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    appointments_today = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.start_at >= today_start, Appointment.start_at <= today_end)
        .scalar()
        or 0
    )

    appointments_week = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.start_at >= datetime.now() - timedelta(days=7))
        .scalar()
        or 0
    )

    patients_this_month = (
        db.query(func.count(Patient.id))
        .filter(Patient.created_at >= datetime.now() - timedelta(days=30))
        .scalar()
        or 0
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": {},
            "total_patients": total_patients,
            "appointments_today": appointments_today,
            "appointments_week": appointments_week,
            "patients_this_month": patients_this_month,
        },
    )


# ==================== WEBHOOKS ====================


@app.post("/webhook")
async def webhook_evolution(request: Request):
    """Webhook para recibir mensajes de Evolution API (WhatsApp)"""
    try:
        data = await request.json()

        # Verificar que es un mensaje entrante
        messages = data.get("data", {}).get("messages", [])

        for msg in messages:
            if msg.get("type") == "conversation" or msg.get("type") == "text":
                text = msg.get("body", {}).get("text", {}).get("text", "")
                from_number = (
                    msg.get("key", {})
                    .get("remoteJid", "")
                    .replace("@c.us", "")
                    .replace("@g.us", "")
                )

                if text and from_number:
                    await handle_whatsapp_message(from_number, text)

        return {"status": "ok"}
    except Exception as e:
        print(f"Error en webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/webhook/telegram")
async def webhook_telegram(request: Request):
    """Webhook para Telegram (configurado en BotFather)"""
    try:
        from app.bot import dp, bot
        from aiogram.types import Update

        update_data = await request.json()
        update = Update(**update_data)

        await dp.feed_update(bot=bot, update=update)

        return {"status": "ok"}
    except Exception as e:
        print(f"Error en webhook Telegram: {e}")
        return {"status": "error", "message": str(e)}


# ==================== API REST ====================


@app.get("/api/patients")
async def list_patients(db: Session = Depends(get_db)):
    """Lista todos los pacientes"""
    patients = db.query(Patient).all()
    return [
        {
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "phone": p.phone,
            "obra_social": p.obra_social,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in patients
    ]


@app.get("/api/appointments/today")
async def today_appointments(db: Session = Depends(get_db)):
    """Turnos de hoy"""
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    appointments = (
        db.query(Appointment)
        .filter(Appointment.start_at >= today_start, Appointment.start_at <= today_end)
        .all()
    )

    return [
        {
            "id": a.id,
            "time": a.start_at.strftime("%H:%M"),
            "patient": f"{a.patient.first_name} {a.patient.last_name}"
            if a.patient
            else "N/A",
            "reason": a.reason,
            "status": a.status,
        }
        for a in appointments
    ]


@app.get("/api/stats")
async def stats(db: Session = Depends(get_db)):
    """Estadísticas generales"""
    from sqlalchemy import func

    total_patients = db.query(func.count(Patient.id)).scalar() or 0
    total_appointments = db.query(func.count(Appointment.id)).scalar() or 0
    total_professionals = db.query(func.count(Professional.id)).scalar() or 0

    return {
        "patients": total_patients,
        "appointments": total_appointments,
        "professionals": total_professionals,
    }


# ==================== EJECUCIÓN ====================


@app.get("/odontogram", response_class=HTMLResponse)
async def odontogram():
    """Página del odontograma interactivo"""
    return templates.TemplateResponse("odontogram.html", {"request": {}})


@app.get("/payments", response_class=HTMLResponse)
async def payments():
    """Página de cobros y deudas"""
    return templates.TemplateResponse("payments.html", {"request": {}})


# ==================== API REST - PACIENTES ====================


@app.get("/api/patients/search")
async def search_patients(q: str, db: Session = Depends(get_db)):
    """Buscar pacientes por nombre, DNI o teléfono"""
    patients = (
        db.query(Patient)
        .filter(
            (Patient.first_name.ilike(f"%{q}%"))
            | (Patient.last_name.ilike(f"%{q}%"))
            | (Patient.dni.ilike(f"%{q}%"))
            | (Patient.phone.ilike(f"%{q}%"))
        )
        .limit(10)
        .all()
    )

    return [
        {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "dni": p.dni,
            "phone": p.phone,
            "obra_social": p.obra_social,
            "email": p.email,
        }
        for p in patients
    ]


@app.post("/api/patients")
async def create_patient(patient_data: dict, db: Session = Depends(get_db)):
    """Crear nuevo paciente"""
    patient = Patient(
        first_name=patient_data.get("first_name"),
        last_name=patient_data.get("last_name"),
        dni=patient_data.get("dni"),
        phone=patient_data.get("phone"),
        obra_social=patient_data.get("obra_social", "Particular"),
        email=patient_data.get("email"),
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    return {
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "dni": patient.dni,
        "phone": patient.phone,
        "obra_social": patient.obra_social,
        "email": patient.email,
    }


# ==================== API REST - TRATAMIENTOS ====================


@app.get("/api/patients/{patient_id}/treatments")
async def get_patient_treatments(patient_id: int, db: Session = Depends(get_db)):
    """Obtener tratamientos de un paciente"""
    from app.models import DentalTreatment

    treatments = (
        db.query(DentalTreatment)
        .filter(DentalTreatment.patient_id == patient_id)
        .order_by(DentalTreatment.treatment_date.desc())
        .all()
    )

    return [
        {
            "id": t.id,
            "tooth": t.tooth,
            "face": t.face,
            "treatment_name": t.treatment_name,
            "treatment_type": t.treatment_code,
            "status": t.status,
            "treatment_date": t.treatment_date.isoformat()
            if t.treatment_date
            else None,
            "cost": t.cost or 0,
            "notes": t.notes,
            "professional": t.professional.full_name if t.professional else None,
        }
        for t in treatments
    ]


@app.post("/api/treatments")
async def create_treatment(treatment_data: dict, db: Session = Depends(get_db)):
    """Crear nuevo tratamiento"""
    from app.models import DentalTreatment

    treatment = DentalTreatment(
        patient_id=treatment_data.get("patient_id"),
        tooth=treatment_data.get("tooth"),
        face=treatment_data.get("face"),
        treatment_name=treatment_data.get("treatment_name"),
        treatment_code=treatment_data.get("treatment_type"),
        treatment_price_id=treatment_data.get("treatment_price_id"),
        status=treatment_data.get("status", "done"),
        treatment_date=datetime.strptime(
            treatment_data.get("treatment_date"), "%Y-%m-%d"
        ).date()
        if treatment_data.get("treatment_date")
        else datetime.now().date(),
        cost=treatment_data.get("cost", 0),
        professional_id=treatment_data.get("professional_id"),
        notes=treatment_data.get("notes"),
    )
    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    return {"id": treatment.id, "status": "ok"}


# ==================== API REST - PAGOS ====================


@app.get("/api/payments")
async def list_payments(db: Session = Depends(get_db)):
    """Lista todos los pagos"""
    from app.models import Payment

    payments = db.query(Payment).order_by(Payment.payment_date.desc()).limit(100).all()

    return [
        {
            "id": p.id,
            "patient_id": p.patient_id,
            "patient_name": f"{p.patient.first_name} {p.patient.last_name}"
            if p.patient
            else "N/A",
            "amount": p.amount,
            "payment_method": p.payment_method,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
            "reference": p.reference,
        }
        for p in payments
    ]


@app.post("/api/payments")
async def create_payment(payment_data: dict, db: Session = Depends(get_db)):
    """Crear nuevo pago"""
    from app.models import Payment

    payment = Payment(
        patient_id=payment_data.get("patient_id"),
        amount=payment_data.get("amount"),
        payment_method=payment_data.get("payment_method", "cash"),
        reference=payment_data.get("reference"),
        notes=payment_data.get("notes"),
    )
    db.add(payment)
    db.commit()

    return {"id": payment.id, "status": "ok"}


# ==================== API REST - DEUDAS ====================


@app.get("/api/debts")
async def list_debts(db: Session = Depends(get_db)):
    """Lista todas las deudas"""
    from app.models import Debt

    debts = db.query(Debt).order_by(Debt.created_at.desc()).all()

    return [
        {
            "id": d.id,
            "patient_id": d.patient_id,
            "patient_name": f"{d.patient.first_name} {d.patient.last_name}"
            if d.patient
            else "N/A",
            "description": d.description,
            "amount": d.amount,
            "status": d.status,
            "due_date": d.due_date.isoformat() if d.due_date else None,
        }
        for d in debts
    ]


@app.post("/api/debts")
async def create_debt(debt_data: dict, db: Session = Depends(get_db)):
    """Crear nueva deuda"""
    from app.models import Debt

    debt = Debt(
        patient_id=debt_data.get("patient_id"),
        description=debt_data.get("description"),
        amount=debt_data.get("amount"),
        status=debt_data.get("status", "pending"),
        due_date=datetime.strptime(debt_data["due_date"], "%Y-%m-%d").date()
        if debt_data.get("due_date")
        else None,
        notes=debt_data.get("notes"),
    )
    db.add(debt)
    db.commit()

    return {"id": debt.id, "status": "ok"}


@app.post("/api/debts/{debt_id}/pay")
async def pay_debt(debt_id: int, db: Session = Depends(get_db)):
    """Marcar deuda como pagada"""
    from app.models import Debt

    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if debt:
        debt.status = "paid"
        db.commit()

    return {"status": "ok"}


@app.get("/api/patients/{patient_id}/debts")
async def get_patient_debts(patient_id: int, db: Session = Depends(get_db)):
    """Obtener deudas de un paciente"""
    from app.models import Debt

    debts = (
        db.query(Debt)
        .filter(Debt.patient_id == patient_id, Debt.status != "paid")
        .all()
    )

    return [
        {
            "id": d.id,
            "description": d.description,
            "amount": d.amount,
            "status": d.status,
            "due_date": d.due_date.isoformat() if d.due_date else None,
        }
        for d in debts
    ]


@app.get("/api/patients/{patient_id}/payments")
async def get_patient_payments(patient_id: int, db: Session = Depends(get_db)):
    """Obtener pagos de un paciente"""
    from app.models import Payment

    payments = db.query(Payment).filter(Payment.patient_id == patient_id).all()

    return [
        {
            "id": p.id,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
        }
        for p in payments
    ]


@app.get("/api/patients/account-summary")
async def account_summary(db: Session = Depends(get_db)):
    """Resumen de cuenta de todos los pacientes"""
    from app.models import DentalTreatment, Payment, Debt

    patients = db.query(Patient).all()
    summary = []

    for patient in patients:
        # Total tratamientos
        treatments = (
            db.query(DentalTreatment)
            .filter(DentalTreatment.patient_id == patient.id)
            .all()
        )
        total_treatments = sum(t.cost or 0 for t in treatments)

        # Total pagado
        payments = db.query(Payment).filter(Payment.patient_id == patient.id).all()
        total_paid = sum(p.amount for p in payments)

        # Total deuda
        debts = (
            db.query(Debt)
            .filter(Debt.patient_id == patient.id, Debt.status != "paid")
            .all()
        )
        total_debt = sum(d.amount for d in debts)

        summary.append(
            {
                "patient_id": patient.id,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "treatments_count": len(treatments),
                "total_treatments": total_treatments,
                "total_paid": total_paid,
                "debt": total_debt,
            }
        )

    return summary


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
