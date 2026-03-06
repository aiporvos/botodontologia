from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date

from config import settings
from app.database import engine, init_db, SessionLocal, get_db
from app.admin import setup_admin
from app.handlers.conversation import handle_whatsapp_message
from app.models import (
    Patient, Appointment, Professional, AdminUser,
    DentalTreatment, DentalRecord, Payment, Debt, TreatmentPrice
)
from app.utils.security import get_password_hash, verify_password
from app.auth import create_access_token, get_current_active_user
from app import schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("📦 Inicializando base de datos...")
    init_db()

    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == settings.admin_username).first()
        if not admin:
            admin = AdminUser(
                username=settings.admin_username,
                password_hash=get_password_hash(settings.admin_password),
                role="admin"
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin creado: {settings.admin_username}")
        else:
            # Forzamos la contraseña de settings para asegurar el acceso
            admin.password_hash = get_password_hash(settings.admin_password)
            db.commit()
            print("🔄 Contraseña de admin actualizada por seguridad")

        # Profesionales por defecto
        if db.query(Professional).count() == 0:
            db.add_all([
                Professional(full_name="Dr. Silvestro", specialty="extracciones/implantes/protesis"),
                Professional(full_name="Dra. Murad", specialty="ortodoncia/conductos"),
            ])
            db.commit()
            print("✅ Profesionales creados")
    finally:
        db.close()

    print("🚀 Dental Studio Pro iniciado")
    yield


app = FastAPI(
    title="Dental Studio Pro",
    description="Sistema de gestión odontológica",
    version="2.0.0",
    lifespan=lifespan,
)

from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.admin_password or "dental-studio-secret-key")

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
setup_admin(app, engine)


# ==================== PÁGINAS ====================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard_v2.html", {"request": request})


# ==================== AUTH ====================

@app.post("/api/auth/login", response_model=schemas.Token)
async def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token(data={"sub": user.username, "role": user.role or "admin"})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/auth/me")
async def get_me(current_user: AdminUser = Depends(get_current_active_user)):
    return {"username": current_user.username, "role": current_user.role or "admin"}


# ==================== STATS ====================

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    total_patients = db.query(func.count(Patient.id)).scalar() or 0
    appts_today = db.query(func.count(Appointment.id)).filter(
        Appointment.start_at >= today_start, Appointment.start_at <= today_end
    ).scalar() or 0
    appts_week = db.query(func.count(Appointment.id)).filter(
        Appointment.start_at >= datetime.now() - timedelta(days=7)
    ).scalar() or 0
    new_patients_month = db.query(func.count(Patient.id)).filter(
        Patient.created_at >= datetime.now() - timedelta(days=30)
    ).scalar() or 0
    total_revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0
    total_debt = db.query(func.coalesce(func.sum(Debt.amount), 0)).filter(Debt.status != "paid").scalar() or 0

    return {
        "total_patients": total_patients,
        "appointments_today": appts_today,
        "appointments_week": appts_week,
        "new_patients_month": new_patients_month,
        "total_revenue": total_revenue,
        "total_debt": total_debt,
    }


# ==================== PACIENTES ====================

@app.get("/api/patients", response_model=List[schemas.Patient])
async def list_patients(db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    return db.query(Patient).order_by(Patient.created_at.desc()).all()

@app.get("/api/patients/search", response_model=List[schemas.Patient])
async def search_patients(q: str, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    return db.query(Patient).filter(
        (Patient.first_name.ilike(f"%{q}%")) |
        (Patient.last_name.ilike(f"%{q}%")) |
        (Patient.dni.ilike(f"%{q}%")) |
        (Patient.phone.ilike(f"%{q}%"))
    ).limit(20).all()

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {
        "id": p.id, "first_name": p.first_name, "last_name": p.last_name,
        "dni": p.dni, "phone": p.phone, "email": p.email,
        "obra_social": p.obra_social, "notes": p.notes,
        "created_at": p.created_at.isoformat() if p.created_at else None
    }

@app.post("/api/patients", response_model=schemas.Patient)
async def create_patient(patient_in: schemas.PatientCreate, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    patient = Patient(**patient_in.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

@app.put("/api/patients/{patient_id}")
async def update_patient(patient_id: int, patient_in: schemas.PatientCreate, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    for key, value in patient_in.model_dump(exclude_unset=True).items():
        setattr(p, key, value)
    db.commit()
    return {"status": "ok"}

@app.delete("/api/patients/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    db.delete(p)
    db.commit()
    return {"status": "ok"}


# ==================== TURNOS ====================

@app.get("/api/appointments")
async def list_appointments(db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    appts = db.query(Appointment).order_by(Appointment.start_at.desc()).limit(100).all()
    return [{
        "id": a.id,
        "patient_name": f"{a.patient.first_name} {a.patient.last_name}" if a.patient else "N/A",
        "patient_id": a.patient_id,
        "professional_name": a.professional.full_name if a.professional else "N/A",
        "reason": a.reason, "category": a.category,
        "start_at": a.start_at.isoformat() if a.start_at else None,
        "end_at": a.end_at.isoformat() if a.end_at else None,
        "status": a.status, "channel": a.channel,
    } for a in appts]

@app.get("/api/appointments/today")
async def today_appointments(db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    appts = db.query(Appointment).filter(
        Appointment.start_at >= today_start, Appointment.start_at <= today_end
    ).order_by(Appointment.start_at).all()
    return [{
        "id": a.id,
        "time": a.start_at.strftime("%H:%M") if a.start_at else "",
        "patient_name": f"{a.patient.first_name} {a.patient.last_name}" if a.patient else "N/A",
        "reason": a.reason, "status": a.status, "category": a.category,
    } for a in appts]

@app.post("/api/appointments")
async def create_appointment(data: dict, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    try:
        start_at = datetime.fromisoformat(data["start_at"].replace('Z', '+00:00'))
        appt = Appointment(
            patient_id=data["patient_id"],
            professional_id=data.get("professional_id", 1),
            reason=data.get("reason", "Consulta"),
            category=data.get("category", "consulta"),
            start_at=start_at,
            end_at=start_at + timedelta(minutes=30),
            status="confirmed",
            channel="web"
        )
        db.add(appt)
        db.commit()
        return {"status": "ok", "id": appt.id}
    except Exception as e:
        print(f"Error creating appointment: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/appointments/{appt_id}/cancel")
async def cancel_appointment(appt_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    a = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if a:
        a.status = "cancelled"
        db.commit()
    return {"status": "ok"}


# ==================== TRATAMIENTOS ====================

@app.get("/api/patients/{patient_id}/treatments")
async def get_patient_treatments(patient_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    treatments = db.query(DentalTreatment).filter(
        DentalTreatment.patient_id == patient_id
    ).order_by(DentalTreatment.treatment_date.desc()).all()
    return [{
        "id": t.id, "tooth": t.tooth, "face": t.face,
        "treatment_name": t.treatment_name, "status": t.status,
        "cost": t.cost, "notes": t.notes,
        "treatment_date": t.treatment_date.isoformat() if t.treatment_date else None,
    } for t in treatments]

@app.post("/api/treatments")
async def create_treatment(data: dict, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    t = DentalTreatment(
        patient_id=data["patient_id"],
        tooth=data.get("tooth"),
        face=data.get("face"),
        treatment_name=data.get("treatment_name", ""),
        status=data.get("status", "planned"),
        cost=data.get("cost", 0),
        notes=data.get("notes"),
        treatment_date=date.today()
    )
    db.add(t)
    db.commit()
    return {"status": "ok", "id": t.id}


# ==================== ODONTOGRAMA ====================

@app.get("/api/patients/{patient_id}/odontogram")
async def get_odontogram(patient_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    records = db.query(DentalRecord).filter(DentalRecord.patient_id == patient_id).all()
    treatments = db.query(DentalTreatment).filter(DentalTreatment.patient_id == patient_id).all()
    return {
        "records": [{
            "id": r.id, "tooth": r.tooth, "face": r.face,
            "procedure_name": r.procedure_name, "record_status": r.record_status,
            "record_date": r.record_date.isoformat() if r.record_date else None
        } for r in records],
        "treatments": [{
            "id": t.id, "tooth": t.tooth, "face": t.face,
            "treatment_name": t.treatment_name, "status": t.status,
            "treatment_date": t.treatment_date.isoformat() if t.treatment_date else None
        } for t in treatments]
    }

@app.post("/api/odontogram")
async def save_odontogram_entry(data: dict, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    try:
        record = DentalRecord(
            patient_id=data["patient_id"],
            tooth=data["tooth"],
            face=data.get("face"),
            procedure_name=data.get("procedure_name", ""),
            record_status=data.get("status", "planned"),
            record_date=date.today()
        )
        db.add(record)
        db.commit()
        return {"status": "ok", "id": record.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/odontogram/{record_id}")
async def delete_odontogram_entry(record_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    r = db.query(DentalRecord).filter(DentalRecord.id == record_id).first()
    if r:
        db.delete(r)
        db.commit()
    return {"status": "ok"}


# ==================== PAGOS ====================

@app.get("/api/payments")
async def list_payments(db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    payments = db.query(Payment).order_by(Payment.payment_date.desc()).limit(100).all()
    return [{
        "id": p.id, "patient_id": p.patient_id,
        "patient_name": f"{p.patient.first_name} {p.patient.last_name}" if p.patient else "N/A",
        "amount": p.amount, "payment_method": p.payment_method,
        "reference": p.reference, "notes": p.notes,
        "payment_date": p.payment_date.isoformat() if p.payment_date else None,
    } for p in payments]

@app.get("/api/patients/{patient_id}/payments")
async def get_patient_payments(patient_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    payments = db.query(Payment).filter(Payment.patient_id == patient_id).all()
    return [{
        "id": p.id, "amount": p.amount, "payment_method": p.payment_method,
        "payment_date": p.payment_date.isoformat() if p.payment_date else None,
        "reference": p.reference,
    } for p in payments]

@app.post("/api/payments")
async def create_payment(data: dict, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    p = Payment(
        patient_id=data["patient_id"],
        amount=data["amount"],
        payment_method=data.get("payment_method", "cash"),
        reference=data.get("reference"),
        notes=data.get("notes"),
    )
    db.add(p)
    db.commit()
    return {"status": "ok", "id": p.id}


# ==================== DEUDAS ====================

@app.get("/api/debts")
async def list_debts(db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    debts = db.query(Debt).filter(Debt.status != "paid").order_by(Debt.created_at.desc()).all()
    return [{
        "id": d.id, "patient_id": d.patient_id,
        "patient_name": f"{d.patient.first_name} {d.patient.last_name}" if d.patient else "N/A",
        "description": d.description, "amount": d.amount, "status": d.status,
        "due_date": d.due_date.isoformat() if d.due_date else None,
    } for d in debts]

@app.get("/api/patients/{patient_id}/debts")
async def get_patient_debts(patient_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    debts = db.query(Debt).filter(Debt.patient_id == patient_id, Debt.status != "paid").all()
    return [{
        "id": d.id, "description": d.description, "amount": d.amount,
        "status": d.status, "due_date": d.due_date.isoformat() if d.due_date else None,
    } for d in debts]

@app.post("/api/debts")
async def create_debt(data: dict, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    d = Debt(
        patient_id=data["patient_id"],
        description=data.get("description", ""),
        amount=data["amount"],
        status="pending",
        due_date=date.fromisoformat(data["due_date"]) if data.get("due_date") else None,
    )
    db.add(d)
    db.commit()
    return {"status": "ok", "id": d.id}

@app.put("/api/debts/{debt_id}/pay")
async def pay_debt(debt_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    d = db.query(Debt).filter(Debt.id == debt_id).first()
    if d:
        d.status = "paid"
        db.commit()
    return {"status": "ok"}


# ==================== CUENTA CORRIENTE ====================

@app.get("/api/patients/{patient_id}/account")
async def patient_account(patient_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404)
    treatments = db.query(DentalTreatment).filter(DentalTreatment.patient_id == patient_id).all()
    payments = db.query(Payment).filter(Payment.patient_id == patient_id).all()
    debts = db.query(Debt).filter(Debt.patient_id == patient_id, Debt.status != "paid").all()
    return {
        "patient": f"{p.first_name} {p.last_name}",
        "total_treatments": sum(t.cost or 0 for t in treatments),
        "total_paid": sum(pay.amount for pay in payments),
        "total_debt": sum(d.amount for d in debts),
        "treatments_count": len(treatments),
    }


# ==================== PROFESIONALES ====================

@app.get("/api/professionals")
async def list_professionals(db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    profs = db.query(Professional).filter(Professional.is_active == True).all()
    return [{"id": p.id, "full_name": p.full_name, "specialty": p.specialty} for p in profs]


# ==================== PRECIOS ====================

@app.get("/api/prices")
async def list_prices(db: Session = Depends(get_db), current_user: AdminUser = Depends(get_current_active_user)):
    prices = db.query(TreatmentPrice).filter(TreatmentPrice.is_active == True).all()
    return [{"id": p.id, "code": p.code, "name": p.name, "price": p.price} for p in prices]


# ==================== WEBHOOKS ====================

@app.post("/webhook")
async def webhook_evolution(request: Request):
    try:
        data = await request.json()
        messages = data.get("data", {}).get("messages", [])
        for msg in messages:
            if msg.get("type") in ["conversation", "text"]:
                text = msg.get("body", {}).get("text", {}).get("text", "")
                from_num = msg.get("key", {}).get("remoteJid", "").split("@")[0]
                if text and from_num:
                    await handle_whatsapp_message(from_num, text)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/webhook/telegram")
async def webhook_telegram(request: Request):
    try:
        from app.bot import dp, bot
        from aiogram.types import Update
        update = Update(**await request.json())
        await dp.feed_update(bot=bot, update=update)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
