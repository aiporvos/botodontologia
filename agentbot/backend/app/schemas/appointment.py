from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AppointmentBase(BaseModel):
    patient_id: int
    professional_id: int
    start_at: datetime
    end_at: datetime
    reason: Optional[str] = Field(None, max_length=200)
    category: str = Field(default="consulta")
    status: str = Field(default="pending")
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    professional_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    id: int
    channel: str
    patient_name: Optional[str] = None
    professional_name: Optional[str] = None

    class Config:
        from_attributes = True
