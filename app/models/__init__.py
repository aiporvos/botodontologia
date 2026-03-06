from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Time,
    Date,
    Index,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    dni = Column(String(20), index=True)
    obra_social = Column(String(100))
    phone = Column(String(20), index=True)
    email = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    appointments = relationship("Appointment", back_populates="patient")
    dental_records = relationship("DentalRecord", back_populates="patient")
    dental_treatments = relationship("DentalTreatment", back_populates="patient")
    payments = relationship("Payment", back_populates="patient")
    debts = relationship("Debt", back_populates="patient")
    consents = relationship("Consent", back_populates="patient")


class Professional(Base):
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    specialty = Column(String(100), nullable=False)
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    availabilities = relationship("Availability", back_populates="professional")
    appointments = relationship("Appointment", back_populates="professional")
    dental_records = relationship("DentalRecord", back_populates="professional")


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1=Lunes, 7=Domingo
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_minutes = Column(Integer, default=30)

    professional = relationship("Professional", back_populates="availabilities")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=False)
    cal_booking_id = Column(String(100))
    reason = Column(String(200), nullable=False)
    category = Column(
        String(50)
    )  # extracciones, implantes, protesis, ortodoncia, conductos, consulta
    start_at = Column(DateTime(timezone=True), nullable=False, index=True)
    end_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        String(20), default="pending"
    )  # pending, confirmed, cancelled, rescheduled, no_show, done
    channel = Column(String(20), default="telegram")  # telegram, whatsapp, web, phone
    calendar_event_id = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="appointments")
    professional = relationship("Professional", back_populates="appointments")

    __table_args__ = (Index("idx_appt_prof_start", "professional_id", "start_at"),)


class DentalRecord(Base):
    __tablename__ = "dental_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    tooth = Column(
        String(10)
    )  # 11-18, 21-28, 31-38, 41-48 (adulto) o 51-55, 61-65, 71-75, 81-85 (niño)
    face = Column(String(10))  # M=Mesial, D=Distal, V=Vestibular, L=Lingual, O=Oclusal
    procedure_code = Column(String(20))
    procedure_name = Column(String(200), nullable=False)
    record_status = Column(String(20), default="planned")  # planned, in_progress, done
    record_date = Column(Date, default="current_date")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="dental_records")
    professional = relationship("Professional", back_populates="dental_records")


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    consent_type = Column(
        String(50), nullable=False
    )  # general, ortodoncia, implante, endodoncia, etc.
    text_version = Column(String(50), nullable=False)
    accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime(timezone=True))
    evidence = Column(String(200))  # telegram_message_id, whatsapp_message_id, pdf_url
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="consents")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    chat_id = Column(String(50), primary_key=True)
    channel = Column(String(20), nullable=False)  # telegram, whatsapp
    step = Column(
        String(30), nullable=False
    )  # ask_name, ask_obra, ask_reason, ask_phone, choose_slot, confirmed
    payload = Column(Text, default="{}")  # JSON string con datos收集
    patient_id = Column(Integer, ForeignKey("patients.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default="admin") # admin, professional, reception
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TreatmentPrice(Base):
    """Catálogo de precios de tratamientos"""

    __tablename__ = "treatment_prices"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True)  # Código del tratamiento
    name = Column(String(200), nullable=False)  # Nombre del tratamiento
    description = Column(Text)
    price = Column(Integer)  # Precio en centavos
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DentalTreatment(Base):
    """Tratamientos realizados en cada diente/cara"""

    __tablename__ = "dental_treatments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("professionals.id"))

    # Diente y cara
    tooth = Column(String(10))  # 11-48 (adulto)
    face = Column(String(10))  # M, O, D, V, P

    # Tratamiento
    treatment_code = Column(String(20))  # FK a treatment_prices
    treatment_name = Column(String(200), nullable=False)
    treatment_price_id = Column(Integer, ForeignKey("treatment_prices.id"))

    # Estado y fecha
    status = Column(String(20), default="planned")  # planned, in_progress, done
    treatment_date = Column(Date)
    notes = Column(Text)

    # Coste
    cost = Column(Integer)  # Precio cobrado

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="dental_treatments")
    professional = relationship("Professional")
    price = relationship("TreatmentPrice")


class Payment(Base):
    """Cobros realizados"""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))

    amount = Column(Integer, nullable=False)  # Monto en centavos
    payment_method = Column(String(20))  # cash, card, transfer, insurance
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    reference = Column(String(100))  # Número de transacción
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="payments")
    appointment = relationship("Appointment")


class Debt(Base):
    """Deudas/Pendientes de pacientes"""

    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    dental_treatment_id = Column(Integer, ForeignKey("dental_treatments.id"))

    description = Column(String(200), nullable=False)
    amount = Column(Integer, nullable=False)  # Monto en centavos
    status = Column(String(20), default="pending")  # pending, partial, paid
    due_date = Column(Date)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    patient = relationship("Patient", back_populates="debts")
