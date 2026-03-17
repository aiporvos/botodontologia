from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class PaymentBase(BaseModel):
    patient_id: int
    amount: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = Field(default="efectivo")
    reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    payment_date: str
    patient_name: Optional[str] = None

    class Config:
        from_attributes = True
