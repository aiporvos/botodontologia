from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date, time
from typing import Optional, List

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    dni: Optional[str] = None
    obra_social: Optional[str] = "Particular"
    phone: str
    email: Optional[EmailStr] = None
    notes: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProfessionalBase(BaseModel):
    full_name: str
    specialty: str
    location: Optional[str] = None
    is_active: bool = True

class Professional(ProfessionalBase):
    id: int
    
    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    patient_id: int
    professional_id: int
    reason: str
    category: Optional[str] = "consulta"
    start_at: datetime
    end_at: datetime
    status: str = "pending"
    channel: str = "telegram"
    notes: Optional[str] = None

class AppointmentCreate(BaseModel):
    patient_id: int
    professional_id: int
    reason: str
    start_at: datetime
    end_at: datetime

class Appointment(AppointmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TreatmentPriceBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    price: int # en centavos

class TreatmentPrice(TreatmentPriceBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class DentalTreatmentBase(BaseModel):
    patient_id: int
    professional_id: Optional[int] = None
    tooth: Optional[str] = None
    face: Optional[str] = None
    treatment_code: Optional[str] = None
    treatment_name: str
    treatment_price_id: Optional[int] = None
    status: str = "planned"
    treatment_date: date
    notes: Optional[str] = None
    cost: int = 0

class DentalTreatment(DentalTreatmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    amount: int
    payment_method: str
    reference: Optional[str] = None
    notes: Optional[str] = None

class Payment(PaymentBase):
    id: int
    payment_date: datetime

    class Config:
        from_attributes = True

class DebtBase(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    dental_treatment_id: Optional[int] = None
    description: str
    amount: int
    status: str = "pending"
    due_date: Optional[date] = None

class Debt(DebtBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
