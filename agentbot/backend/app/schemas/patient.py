from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PatientBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    dni: Optional[str] = Field(None, max_length=20)
    phone: str = Field(..., max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    obra_social: Optional[str] = Field(default="Particular")
    address: Optional[str] = None
    birth_date: Optional[date] = None
    notes: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class PatientResponse(PatientBase):
    id: int
    full_name: str
    created_at: str

    class Config:
        from_attributes = True
