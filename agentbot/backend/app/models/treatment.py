from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=False)
    tooth = Column(String(10))  # Número de diente
    surface = Column(String(20))  # top, bottom, left, right, center
    treatment_type = Column(
        String(100), nullable=False
    )  # caries, conducto, extraccion, etc.
    description = Column(Text)
    cost = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="planned")  # planned, in_progress, completed
    treatment_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="treatments")
    professional = relationship("Professional", back_populates="treatments")

    def __repr__(self):
        return f"<Treatment {self.treatment_type} - Tooth {self.tooth}>"
