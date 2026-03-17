from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Professional(Base):
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    license_number = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    availabilities = relationship(
        "Availability", back_populates="professional", cascade="all, delete-orphan"
    )
    appointments = relationship("Appointment", back_populates="professional")
    treatments = relationship("Treatment", back_populates="professional")

    def __repr__(self):
        return f"<Professional {self.full_name}>"
