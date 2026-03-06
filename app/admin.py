from sqladmin import Admin, ModelView
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import engine
from app.models import (
    Patient,
    Professional,
    Availability,
    Appointment,
    DentalRecord,
    DentalTreatment,
    Consent,
    ChatSession,
    AdminUser,
    TreatmentPrice,
    Payment,
    Debt,
)


class PatientAdmin(ModelView, model=Patient):
    """Administración de Pacientes"""

    column_list = [
        Patient.id,
        Patient.first_name,
        Patient.last_name,
        Patient.phone,
        Patient.obra_social,
        Patient.created_at,
    ]
    column_searchable = [
        Patient.first_name,
        Patient.last_name,
        Patient.phone,
        Patient.dni,
    ]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Paciente"
    name_plural = "Pacientes"


class ProfessionalAdmin(ModelView, model=Professional):
    """Administración de Profesionales"""

    column_list = [
        Professional.id,
        Professional.full_name,
        Professional.specialty,
        Professional.is_active,
    ]
    column_searchable = [Professional.full_name, Professional.specialty]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Profesional"
    name_plural = "Profesionales"


class AvailabilityAdmin(ModelView, model=Availability):
    """Administración de Disponibilidad"""

    column_list = [
        Availability.id,
        Availability.professional_id,
        Availability.day_of_week,
        Availability.start_time,
        Availability.end_time,
    ]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Disponibilidad"
    name_plural = "Disponibilidades"


class AppointmentAdmin(ModelView, model=Appointment):
    """Administración de Turnos"""

    column_list = [
        Appointment.id,
        Appointment.patient_id,
        Appointment.professional_id,
        Appointment.start_at,
        Appointment.status,
        Appointment.category,
    ]
    column_searchable = [Appointment.reason, Appointment.category]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Turno"
    name_plural = "Turnos"


class DentalRecordAdmin(ModelView, model=DentalRecord):
    """Administración de Registros Dentales (Odontograma)"""

    column_list = [
        DentalRecord.id,
        DentalRecord.patient_id,
        DentalRecord.tooth,
        DentalRecord.procedure_name,
        DentalRecord.record_status,
    ]
    column_searchable = [DentalRecord.tooth, DentalRecord.procedure_name]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Registro Dental"
    name_plural = "Registros Dentales"


class ConsentAdmin(ModelView, model=Consent):
    """Administración de Consentimientos"""

    column_list = [
        Consent.id,
        Consent.patient_id,
        Consent.consent_type,
        Consent.accepted,
        Consent.accepted_at,
    ]
    column_searchable = [Consent.consent_type]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Consentimiento"
    name_plural = "Consentimientos"


class ChatSessionAdmin(ModelView, model=ChatSession):
    """Administración de Sesiones de Chat"""

    column_list = [
        ChatSession.chat_id,
        ChatSession.channel,
        ChatSession.step,
        ChatSession.updated_at,
    ]
    can_delete = True
    can_edit = False
    can_create = False
    can_view_details = True
    name = "Sesión Chat"
    name_plural = "Sesiones Chat"


class TreatmentPriceAdmin(ModelView, model=TreatmentPrice):
    """Administración de Precios de Tratamientos"""

    column_list = [
        TreatmentPrice.id,
        TreatmentPrice.code,
        TreatmentPrice.name,
        TreatmentPrice.price,
        TreatmentPrice.is_active,
    ]
    column_searchable = [TreatmentPrice.code, TreatmentPrice.name]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Precio Tratamiento"
    name_plural = "Precios Tratamientos"


class DentalTreatmentAdmin(ModelView, model=DentalTreatment):
    """Administración de Tratamientos Dentales"""

    column_list = [
        DentalTreatment.id,
        DentalTreatment.patient_id,
        DentalTreatment.tooth,
        DentalTreatment.face,
        DentalTreatment.treatment_name,
        DentalTreatment.status,
        DentalTreatment.treatment_date,
    ]
    column_searchable = [DentalTreatment.tooth, DentalTreatment.treatment_name]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Tratamiento Dental"
    name_plural = "Tratamientos Dentales"


class PaymentAdmin(ModelView, model=Payment):
    """Administración de Cobros"""

    column_list = [
        Payment.id,
        Payment.patient_id,
        Payment.amount,
        Payment.payment_method,
        Payment.payment_date,
    ]
    column_searchable = [Payment.reference]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Cobro"
    name_plural = "Cobros"


class DebtAdmin(ModelView, model=Debt):
    """Administración de Deudas"""

    column_list = [
        Debt.id,
        Debt.patient_id,
        Debt.description,
        Debt.amount,
        Debt.status,
        Debt.due_date,
    ]
    column_searchable = [Debt.description]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Deuda"
    name_plural = "Deudas"


class AdminUserAdmin(ModelView, model=AdminUser):
    """Administración de Usuarios del Panel"""

    column_list = [AdminUser.id, AdminUser.username, AdminUser.is_active, AdminUser.created_at]
    form_excluded_columns = [AdminUser.password_hash]
    column_details_exclude_list = [AdminUser.password_hash]
    can_delete = True
    can_edit = True
    can_create = True
    name = "Usuario Admin"
    name_plural = "Usuarios Admin"


def setup_admin(app, engine):
    """Configura el panel de administración"""
    from sqladmin.authentication import AuthenticationBackend
    from starlette.requests import Request
    from starlette.responses import RedirectResponse
    from config import settings

    class AdminAuth(AuthenticationBackend):
        async def login(self, request: Request) -> bool:
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
            if username == settings.admin_username and password == settings.admin_password:
                request.session.update({"token": "authenticated"})
                return True
            return False

        async def logout(self, request: Request) -> bool:
            request.session.clear()
            return True

        async def authenticate(self, request: Request) -> bool:
            token = request.session.get("token")
            if not token:
                return False
            return True

    auth_backend = AdminAuth(secret_key=settings.admin_password[:32] if len(settings.admin_password) > 32 else settings.admin_password + "x" * (32 - len(settings.admin_password)))

    admin = Admin(
        app,
        engine,
        title="Dental Studio Pro - Admin",
        base_url="/admin",
        authentication_backend=auth_backend,
    )

    admin.add_view(PatientAdmin)
    admin.add_view(ProfessionalAdmin)
    admin.add_view(AvailabilityAdmin)
    admin.add_view(AppointmentAdmin)
    admin.add_view(DentalRecordAdmin)
    admin.add_view(DentalTreatmentAdmin)
    admin.add_view(ConsentAdmin)
    admin.add_view(ChatSessionAdmin)
    admin.add_view(AdminUserAdmin)
    admin.add_view(TreatmentPriceAdmin)
    admin.add_view(PaymentAdmin)
    admin.add_view(DebtAdmin)

    return admin

