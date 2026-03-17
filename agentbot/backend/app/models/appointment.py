from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String(200))
    category = Column(String(50), default="consulta")
    status = Column(
        String(20), default="pending"
    )  # pending, confirmed, cancelled, completed
    channel = Column(String(20), default="web")  # web, whatsapp, telegram
    notes = Column(Text)
    reminder_sent = Column(String(1), default="0")  # 0=no, 1=yes
    confirmation_status = Column(
        String(20), default="pending"
    )  # pending, confirmed, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    professional = relationship("Professional", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment {self.id} - {self.patient.full_name if self.patient else 'Unknown'}>"
