from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Patient, AdminUser
from app.auth import get_current_active_user
from app import schemas

router = APIRouter(prefix="/api/patients", tags=["patients"])

@router.get("/", response_model=List[schemas.Patient])
async def list_patients(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    return db.query(Patient).order_by(Patient.created_at.desc()).all()

@router.get("/search", response_model=List[schemas.Patient])
async def search_patients(
    q: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    return (
        db.query(Patient)
        .filter(
            (Patient.first_name.ilike(f"%{q}%"))
            | (Patient.last_name.ilike(f"%{q}%"))
            | (Patient.dni.ilike(f"%{q}%"))
            | (Patient.phone.ilike(f"%{q}%"))
        )
        .limit(20)
        .all()
    )

@router.get("/{patient_id}")
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {
        "id": p.id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "dni": p.dni,
        "phone": p.phone,
        "email": p.email,
        "obra_social": p.obra_social,
        "notes": p.notes,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }

@router.post("/", response_model=schemas.Patient)
async def create_patient(
    patient_in: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    patient = Patient(**patient_in.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

@router.put("/{patient_id}")
async def update_patient(
    patient_id: int,
    patient_in: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    for key, value in patient_in.model_dump(exclude_unset=True).items():
        setattr(p, key, value)
    db.commit()
    return {"status": "ok"}

@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    db.delete(p)
    db.commit()
    return {"status": "ok"}
