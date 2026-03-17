from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models import Appointment, AdminUser, Professional
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

@router.get("/")
async def list_appointments(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    appts = db.query(Appointment).order_by(Appointment.start_at.desc()).limit(100).all()
    return [
        {
            "id": a.id,
            "patient_name": f"{a.patient.first_name} {a.patient.last_name}"
            if a.patient
            else "N/A",
            "patient_id": a.patient_id,
            "professional_name": a.professional.full_name if a.professional else "N/A",
            "reason": a.reason,
            "category": a.category,
            "start_at": a.start_at.isoformat() if a.start_at else None,
            "end_at": a.end_at.isoformat() if a.end_at else None,
            "status": a.status,
            "channel": a.channel,
        }
        for a in appts
    ]

@router.get("/today")
async def today_appointments(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    try:
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        appts = (
            db.query(Appointment)
            .options(joinedload(Appointment.patient))
            .filter(
                Appointment.start_at >= today_start, Appointment.start_at <= today_end
            )
            .order_by(Appointment.start_at)
            .all()
        )

        result = []
        for a in appts:
            try:
                patient_name = "N/A"
                if a.patient:
                    first = a.patient.first_name or ""
                    last = a.patient.last_name or ""
                    patient_name = f"{first} {last}".strip() or "N/A"

                result.append(
                    {
                        "id": a.id,
                        "time": a.start_at.strftime("%H:%M") if a.start_at else "",
                        "patient_name": patient_name,
                        "patient_phone": a.patient.phone if a.patient else None,
                        "reason": a.reason or "Consulta",
                        "status": a.status or "pending",
                        "category": a.category or "consulta",
                    }
                )
            except Exception as e:
                print(f"Error procesando appointment {a.id}: {e}")
                continue

        return result
    except Exception as e:
        print(f"Error en today_appointments: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cargar turnos: {str(e)}")

@router.post("/")
async def create_appointment(
    data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    try:
        start_at_str = data["start_at"]
        if "Z" in start_at_str:
            start_at = datetime.fromisoformat(start_at_str.replace("Z", "+00:00"))
        else:
            start_at = datetime.fromisoformat(start_at_str)

        appt = Appointment(
            patient_id=data["patient_id"],
            professional_id=data.get("professional_id", 1),
            reason=data.get("reason", "Consulta"),
            category=data.get("category", "consulta"),
            start_at=start_at,
            end_at=start_at + timedelta(minutes=30),
            status="confirmed",
            channel="web",
        )
        db.add(appt)
        db.commit()
        return {"status": "ok", "id": appt.id}
    except Exception as e:
        print(f"Error creating appointment: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{appt_id}")
async def update_appointment(
    appt_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    a = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    if "start_at" in data:
        start_at_str = data["start_at"]
        if "Z" in start_at_str:
            a.start_at = datetime.fromisoformat(start_at_str.replace("Z", "+00:00"))
        else:
            a.start_at = datetime.fromisoformat(start_at_str)
        a.end_at = a.start_at + timedelta(minutes=30)

    if "reason" in data:
        a.reason = data["reason"]
    if "category" in data:
        a.category = data["category"]
    if "professional_id" in data:
        a.professional_id = data["professional_id"]
    if "status" in data:
        a.status = data["status"]

    db.commit()
    return {"status": "ok"}

@router.put("/{appt_id}/cancel")
async def cancel_appointment(
    appt_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    a = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if a:
        a.status = "cancelled"
        db.commit()
    return {"status": "ok"}
