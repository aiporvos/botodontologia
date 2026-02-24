from sqlalchemy.orm import Session
from app.models import Patient
import re


def normalize_ar_phone(raw: str) -> str:
    """Normaliza número de teléfono argentino"""
    if not raw:
        return ""
    s = raw.strip()
    s = re.sub(r"[^\d+]", "", s)

    if s.startswith("0"):
        s = s[1:]
    if s.startswith("54"):
        s = "+" + s
    if not s.startswith("+"):
        s = "+54" + s

    return s


def clean_text(s: str) -> str:
    """Limpia texto de espacios extras"""
    return (s or "").strip()


def get_or_create_patient(
    db: Session,
    phone: str,
    first_name: str = None,
    last_name: str = None,
    dni: str = None,
    obra_social: str = None,
    email: str = None,
):
    """Busca paciente por teléfono o crea uno nuevo"""
    phone = normalize_ar_phone(phone)

    patient = db.query(Patient).filter(Patient.phone == phone).first()

    if patient:
        # Actualizar datos si vienen nuevos
        if first_name:
            patient.first_name = first_name
        if last_name:
            patient.last_name = last_name
        if dni:
            patient.dni = dni
        if obra_social:
            patient.obra_social = obra_social
        if email:
            patient.email = email
        db.commit()
        db.refresh(patient)
    else:
        patient = Patient(
            first_name=first_name or "Paciente",
            last_name=last_name or "",
            phone=phone,
            dni=dni,
            obra_social=obra_social,
            email=email,
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

    return patient
