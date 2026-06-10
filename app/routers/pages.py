from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Appointment
from app.services.evolution import evolution_service
from config import settings

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/schedule", response_class=HTMLResponse)
async def schedule_page(request: Request):
    return templates.TemplateResponse("schedule.html", {"request": request})

@router.get("/odontogram", response_class=HTMLResponse)
async def odontogram_page(request: Request):
    return templates.TemplateResponse("odontogram.html", {"request": request})

@router.get("/patients", response_class=HTMLResponse)
async def patients_page(request: Request):
    return templates.TemplateResponse("patients.html", {"request": request})

@router.get("/payments", response_class=HTMLResponse)
async def payments_page(request: Request):
    return templates.TemplateResponse("payments.html", {"request": request})

@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})

@router.get("/turnos/{appt_id}/cancelar", response_class=HTMLResponse)
async def cancel_appointment_public(appt_id: int, request: Request, db: Session = Depends(get_db)):
    a = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not a:
        return HTMLResponse("<h1>Turno no encontrado</h1>", status_code=404)
        
    if a.status == "cancelled":
        return HTMLResponse("<h1>Este turno ya estaba cancelado.</h1>")
        
    # Cancelar turno
    a.status = "cancelled"
    db.commit()
    
    # Notificar a secretarias/admin
    patient_name = f"{a.patient.first_name} {a.patient.last_name}" if a.patient else "Desconocido"
    date_str = a.start_at.strftime("%d/%m/%Y a las %H:%M") if a.start_at else "Desconocida"
    msg = f"⚠️ *TURNO CANCELADO*\n\nEl paciente *{patient_name}* acaba de cancelar su turno del *{date_str}* (Motivo original: {a.reason})."
    
    admin_numbers = [num.strip() for num in settings.admin_notification_numbers.split(",") if num.strip()]
    for number in admin_numbers:
        try:
            # Requires await, but we don't want to block the response
            import asyncio
            asyncio.create_task(evolution_service.send_text(number, msg))
        except:
            pass
            
    return HTMLResponse(
        "<h1>Turno Cancelado Exitosamente</h1>"
        "<p>Tu turno ha sido cancelado. Si deseas reprogramar, por favor comunícate nuevamente con el bot o la clínica.</p>"
    )
