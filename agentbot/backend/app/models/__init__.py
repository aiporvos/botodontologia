from app.core.database import Base

# Import all models to register them with SQLAlchemy
from app.models.user import User
from app.models.patient import Patient
from app.models.professional import Professional
from app.models.availability import Availability
from app.models.appointment import Appointment
from app.models.treatment import Treatment
from app.models.payment import Payment
from app.models.debt import Debt

__all__ = [
    "Base",
    "User",
    "Patient",
    "Professional",
    "Availability",
    "Appointment",
    "Treatment",
    "Payment",
    "Debt",
]
