from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50))  # efectivo, tarjeta, transferencia
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    reference = Column(String(100))
    notes = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="payments")

    def __repr__(self):
        return f"<Payment ${self.amount} - {self.patient.full_name if self.patient else 'Unknown'}>"
