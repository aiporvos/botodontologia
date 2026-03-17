from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.database import get_db
from app.models import Payment, Debt, DentalTreatment, AdminUser
from app.auth import get_current_active_user

router = APIRouter(prefix="/api", tags=["payments_and_treatments"])

# ==================== TRATAMIENTOS ====================

@router.get("/patients/{patient_id}/treatments")
async def get_patient_treatments(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
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
            "status": t.status,
            "cost": t.cost,
            "notes": t.notes,
            "treatment_date": t.treatment_date.isoformat()
            if t.treatment_date
            else None,
        }
        for t in treatments
    ]

@router.post("/treatments")
async def create_treatment(
    data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    t = DentalTreatment(
        patient_id=data["patient_id"],
        tooth=data.get("tooth"),
        face=data.get("face"),
        treatment_name=data.get("treatment_name", ""),
        status=data.get("status", "planned"),
        cost=data.get("cost", 0),
        notes=data.get("notes"),
        treatment_date=date.today(),
    )
    db.add(t)
    db.commit()
    return {"status": "ok", "id": t.id}

# ==================== PAGOS ====================

@router.get("/payments")
async def list_payments(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
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
            "reference": p.reference,
            "notes": p.notes,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
        }
        for p in payments
    ]

@router.get("/patients/{patient_id}/payments")
async def get_patient_payments(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    payments = db.query(Payment).filter(Payment.patient_id == patient_id).all()
    return [
        {
            "id": p.id,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
            "reference": p.reference,
        }
        for p in payments
    ]

@router.post("/payments")
async def create_payment(
    data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
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

@router.get("/debts")
async def list_debts(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    debts = (
        db.query(Debt)
        .order_by(Debt.created_at.desc())
        .limit(100)
        .all()
    )
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
