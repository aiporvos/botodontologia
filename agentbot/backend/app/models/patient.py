from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, index=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(100))
    obra_social = Column(String(100), default="Particular")
    address = Column(Text)
    birth_date = Column(Date)
    notes = Column(Text)
    odontogram_data = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    appointments = relationship(
        "Appointment", back_populates="patient", cascade="all, delete-orphan"
    )
    treatments = relationship(
        "Treatment", back_populates="patient", cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payment", back_populates="patient", cascade="all, delete-orphan"
    )
    debts = relationship("Debt", back_populates="patient", cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Patient {self.full_name}>"
