from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date


class DebtBase(BaseModel):
    patient_id: int
    amount: Decimal = Field(..., gt=0)
    due_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=255)


class DebtCreate(DebtBase):
    pass


class DebtResponse(DebtBase):
    id: int
    status: str
    created_at: str
    patient_name: Optional[str] = None

    class Config:
        from_attributes = True
