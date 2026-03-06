from pydantic import BaseModel, Field, validator
from datetime import datetime, date, time
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    dni: Optional[str] = None
    obra_social: Optional[str] = "Particular"
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None

    @validator('email', pre=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v

    @validator('phone', 'dni', 'obra_social', 'notes', pre=True)
    def clean_empty(cls, v):
        if v == '':
            return None
        return v

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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

class Appointment(AppointmentBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TreatmentPriceBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    price: int

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
    treatment_name: str
    status: str = "planned"
    treatment_date: Optional[date] = None
    notes: Optional[str] = None
    cost: Optional[int] = 0

class DentalTreatment(DentalTreatmentBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    patient_id: int
    amount: int
    payment_method: Optional[str] = "cash"
    reference: Optional[str] = None
    notes: Optional[str] = None

class Payment(PaymentBase):
    id: int
    payment_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class DebtBase(BaseModel):
    patient_id: int
    description: str
    amount: int
    status: str = "pending"
    due_date: Optional[date] = None

class Debt(DebtBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
