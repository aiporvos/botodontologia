from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date


class TreatmentBase(BaseModel):
    patient_id: int
    professional_id: int
    tooth: Optional[str] = Field(None, max_length=10)
    surface: Optional[str] = Field(None, max_length=20)
    treatment_type: str = Field(..., max_length=100)
    description: Optional[str] = None
    cost: Decimal = Field(default=0, ge=0)
    status: str = Field(default="planned")
    treatment_date: Optional[date] = None


class TreatmentCreate(TreatmentBase):
    pass


class TreatmentResponse(TreatmentBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True
