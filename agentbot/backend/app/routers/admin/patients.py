from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.routers.clinic.auth import get_current_user
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.models.patient import Patient
from app.models.user import User

router = APIRouter(prefix="/patients", tags=["patients"])


def check_admin_or_recepcion(current_user: User):
    if current_user.role not in ["admin", "recepcion"]:
        raise HTTPException(status_code=403, detail="No tiene permisos")


@router.get("/", response_model=List[PatientResponse])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List patients with pagination and search"""
    check_admin_or_recepcion(current_user)

    query = db.query(Patient)

    if search:
        query = query.filter(
            (Patient.first_name.ilike(f"%{search}%"))
            | (Patient.last_name.ilike(f"%{search}%"))
            | (Patient.dni.ilike(f"%{search}%"))
            | (Patient.phone.ilike(f"%{search}%"))
        )

    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=PatientResponse)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new patient"""
    check_admin_or_recepcion(current_user)

    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get patient by ID"""
    check_admin_or_recepcion(current_user)

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update patient"""
    check_admin_or_recepcion(current_user)

    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    update_data = patient_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete patient (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Solo administradores pueden eliminar"
        )

    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    db.delete(db_patient)
    db.commit()
    return {"message": "Paciente eliminado correctamente"}
