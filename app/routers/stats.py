from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Patient, Appointment, Payment, Debt, AdminUser
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("/")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    total_patients = db.query(func.count(Patient.id)).scalar() or 0
    appts_today = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.start_at >= today_start, Appointment.start_at <= today_end)
        .scalar()
        or 0
    )
    appts_week = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.start_at >= datetime.now() - timedelta(days=7))
        .scalar()
        or 0
    )
    new_patients_month = (
        db.query(func.count(Patient.id))
        .filter(Patient.created_at >= datetime.now() - timedelta(days=30))
        .scalar()
        or 0
    )
    total_revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0
    total_debt = (
        db.query(func.coalesce(func.sum(Debt.amount), 0))
        .filter(Debt.status != "paid")
        .scalar()
        or 0
    )

    return {
        "total_patients": total_patients,
        "appointments_today": appts_today,
        "appointments_week": appts_week,
        "new_patients_month": new_patients_month,
        "total_revenue": total_revenue,
        "total_debt": total_debt,
    }
