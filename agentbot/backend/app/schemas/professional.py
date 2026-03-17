from pydantic import BaseModel, Field
from typing import Optional


class ProfessionalBase(BaseModel):
    full_name: str = Field(..., max_length=100)
    specialty: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    license_number: Optional[str] = Field(None, max_length=50)


class ProfessionalCreate(ProfessionalBase):
    pass


class ProfessionalResponse(ProfessionalBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
