from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.core.database import Base


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1=Lunes, 7=Domingo
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_minutes = Column(Integer, default=30)

    # Relationships
    professional = relationship("Professional", back_populates="availabilities")

    def __repr__(self):
        return f"<Availability {self.professional.full_name} - Day {self.day_of_week}>"
