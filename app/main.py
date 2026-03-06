from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from config import settings
from app.database import engine, init_db, SessionLocal, get_db
from app.admin import setup_admin
from app.handlers.conversation import handle_whatsapp_message
from app.models import Patient, Appointment, Professional, AdminUser
from app.utils.security import get_password_hash
from app import schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización al iniciar la app"""
    print("📦 Inicializando base de datos...")
    init_db()

    # Crear admin por defecto si no existe
    db = SessionLocal()
    try:
        admin = (
            db.query(AdminUser)
            .filter(AdminUser.username == settings.admin_username)
            .first()
        )
        if not admin:
            hashed_pw = get_password_hash(settings.admin_password)
            admin = AdminUser(
                username=settings.admin_username, password_hash=hashed_pw
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
from sqlalchemy.orm import Session


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


@app.get("/api/patients", response_model=List[schemas.Patient])
async def list_patients(db: Session = Depends(get_db)):
    """Lista todos los pacientes"""
    return db.query(Patient).all()


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


@app.get("/api/patients/search", response_model=List[schemas.Patient])
async def search_patients(q: str, db: Session = Depends(get_db)):
    """Buscar pacientes por nombre, DNI o teléfono"""
    return (
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


@app.post("/api/patients", response_model=schemas.Patient)
async def create_patient(patient_in: schemas.PatientCreate, db: Session = Depends(get_db)):
    """Crear nuevo paciente"""
    patient = Patient(**patient_in.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


# ==================== API REST - TRATAMIENTOS ====================


@app.get("/api/patients/{patient_id}/treatments", response_model=List[schemas.DentalTreatment])
async def get_patient_treatments(patient_id: int, db: Session = Depends(get_db)):
    """Obtener tratamientos de un paciente"""
    from app.models import DentalTreatment

    return (
        db.query(DentalTreatment)
        .filter(DentalTreatment.patient_id == patient_id)
        .order_by(DentalTreatment.treatment_date.desc())
        .all()
    )


@app.post("/api/treatments", response_model=schemas.DentalTreatment)
async def create_treatment(treatment_in: schemas.DentalTreatmentBase, db: Session = Depends(get_db)):
    """Crear nuevo tratamiento"""
    from app.models import DentalTreatment

    treatment = DentalTreatment(**treatment_in.model_dump())
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment


# ==================== API REST - PAGOS ====================


@app.get("/api/payments", response_model=List[schemas.Payment])
async def list_payments(db: Session = Depends(get_db)):
    """Lista todos los pagos"""
    from app.models import Payment

    return db.query(Payment).order_by(Payment.payment_date.desc()).limit(100).all()


@app.post("/api/payments", response_model=schemas.Payment)
async def create_payment(payment_in: schemas.PaymentBase, db: Session = Depends(get_db)):
    """Crear nuevo pago"""
    from app.models import Payment

    payment = Payment(**payment_in.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


# ==================== API REST - DEUDAS ====================


@app.get("/api/debts", response_model=List[schemas.Debt])
async def list_debts(db: Session = Depends(get_db)):
    """Lista todas las deudas"""
    from app.models import Debt

    return db.query(Debt).order_by(Debt.created_at.desc()).all()


@app.post("/api/debts", response_model=schemas.Debt)
async def create_debt(debt_in: schemas.DebtBase, db: Session = Depends(get_db)):
    """Crear nueva deuda"""
    from app.models import Debt

    debt = Debt(**debt_in.model_dump())
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return debt


@app.post("/api/debts/{debt_id}/pay")
async def pay_debt(debt_id: int, db: Session = Depends(get_db)):
    """Marcar deuda como pagada"""
    from app.models import Debt

    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if debt:
        debt.status = "paid"
        db.commit()

    return {"status": "ok"}


@app.get("/api/patients/{patient_id}/debts", response_model=List[schemas.Debt])
async def get_patient_debts(patient_id: int, db: Session = Depends(get_db)):
    """Obtener deudas de un paciente"""
    from app.models import Debt

    return (
        db.query(Debt)
        .filter(Debt.patient_id == patient_id, Debt.status != "paid")
        .all()
    )


@app.get("/api/patients/{patient_id}/payments", response_model=List[schemas.Payment])
async def get_patient_payments(patient_id: int, db: Session = Depends(get_db)):
    """Obtener pagos de un paciente"""
    from app.models import Payment

    return db.query(Payment).filter(Payment.patient_id == patient_id).all()


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

        # Total deuda pendiente
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
