from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.routers.clinic.auth import get_current_user
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.models.appointment import Appointment
from app.models.user import User

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    professional_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List appointments with filters"""
    query = db.query(Appointment)

    if start_date:
        query = query.filter(
            Appointment.start_at >= datetime.combine(start_date, datetime.min.time())
        )

    if end_date:
        query = query.filter(
            Appointment.start_at <= datetime.combine(end_date, datetime.max.time())
        )

    if professional_id:
        query = query.filter(Appointment.professional_id == professional_id)

    if status:
        query = query.filter(Appointment.status == status)

    appointments = (
        query.order_by(Appointment.start_at.desc()).offset(skip).limit(limit).all()
    )

    # Enrich with patient and professional names
    for apt in appointments:
        if apt.patient:
            apt.patient_name = apt.patient.full_name
        if apt.professional:
            apt.professional_name = apt.professional.full_name

    return appointments


@router.get("/today", response_model=List[AppointmentResponse])
def get_today_appointments(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get today's appointments"""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    appointments = (
        db.query(Appointment)
        .filter(Appointment.start_at >= today_start, Appointment.start_at <= today_end)
        .order_by(Appointment.start_at)
        .all()
    )

    for apt in appointments:
        if apt.patient:
            apt.patient_name = apt.patient.full_name
        if apt.professional:
            apt.professional_name = apt.professional.full_name

    return appointments


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new appointment"""
    # Check for conflicts
    existing = (
        db.query(Appointment)
        .filter(
            Appointment.professional_id == appointment.professional_id,
            Appointment.status.in_(["pending", "confirmed"]),
            or_(
                and_(
                    Appointment.start_at < appointment.end_at,
                    Appointment.end_at > appointment.start_at,
                )
            ),
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="El profesional ya tiene un turno en ese horario"
        )

    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    if db_appointment.patient:
        db_appointment.patient_name = db_appointment.patient.full_name
    if db_appointment.professional:
        db_appointment.professional_name = db_appointment.professional.full_name

    return db_appointment


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get appointment by ID"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    if appointment.patient:
        appointment.patient_name = appointment.patient.full_name
    if appointment.professional:
        appointment.professional_name = appointment.professional.full_name

    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update appointment"""
    db_appointment = (
        db.query(Appointment).filter(Appointment.id == appointment_id).first()
    )
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    update_data = appointment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)

    db.commit()
    db.refresh(db_appointment)

    if db_appointment.patient:
        db_appointment.patient_name = db_appointment.patient.full_name
    if db_appointment.professional:
        db_appointment.professional_name = db_appointment.professional.full_name

    return db_appointment


@router.put("/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel appointment"""
    db_appointment = (
        db.query(Appointment).filter(Appointment.id == appointment_id).first()
    )
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    db_appointment.status = "cancelled"
    if reason:
        db_appointment.notes = f"Cancelado: {reason}"

    db.commit()
    return {"message": "Turno cancelado correctamente"}
