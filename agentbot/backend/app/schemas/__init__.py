from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.schemas.professional import ProfessionalCreate, ProfessionalResponse
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.schemas.treatment import TreatmentCreate, TreatmentResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.debt import DebtCreate, DebtResponse

__all__ = [
    "UserCreate",
    "UserResponse",
    "UserLogin",
    "PatientCreate",
    "PatientResponse",
    "PatientUpdate",
    "ProfessionalCreate",
    "ProfessionalResponse",
    "AppointmentCreate",
    "AppointmentResponse",
    "AppointmentUpdate",
    "TreatmentCreate",
    "TreatmentResponse",
    "PaymentCreate",
    "PaymentResponse",
    "DebtCreate",
    "DebtResponse",
]
