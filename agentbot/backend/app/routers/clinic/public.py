from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.routers.clinic.auth import get_current_user
from app.schemas.professional import ProfessionalResponse
from app.schemas.patient import PatientResponse
from app.models.professional import Professional
from app.models.patient import Patient

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/professionals", response_model=List[ProfessionalResponse])
def list_professionals(specialty: Optional[str] = None, db: Session = Depends(get_db)):
    """List active professionals (public endpoint)"""
    query = db.query(Professional).filter(Professional.is_active == True)

    if specialty:
        query = query.filter(Professional.specialty.ilike(f"%{specialty}%"))

    return query.all()


@router.get("/professionals/{professional_id}", response_model=ProfessionalResponse)
def get_professional(professional_id: int, db: Session = Depends(get_db)):
    """Get professional by ID"""
    professional = (
        db.query(Professional)
        .filter(Professional.id == professional_id, Professional.is_active == True)
        .first()
    )

    if not professional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    return professional


@router.get("/patients/search", response_model=List[PatientResponse])
def search_patients(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search patients by name, DNI or phone"""
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
