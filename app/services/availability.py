"""
Sistema de Disponibilidad Real - Dental Studio Pro
Consulta disponibilidad de profesionales considerando:
- Horarios de atención configurados
- Turnos existentes
- Duración variable según tipo de tratamiento
- Feriados y días no laborables
"""

from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import (
    Professional,
    Availability,
    Appointment,
    DentalTreatment,
    TreatmentPrice,
)


class AvailabilityService:
    """Servicio para consultar y gestionar disponibilidad de profesionales"""

    # Duraciones por tipo de tratamiento (en minutos)
    TREATMENT_DURATIONS = {
        "consultation": 15,
        "cleaning": 15,
        "extraction": 30,
        "implant": 90,
        "prosthesis": 30,
        "endodontics": 60,
        "orthodontics": 30,
        "crown": 45,
        "obturation": 30,
        "caries": 30,
        "whitening": 45,
        "periodontics": 45,
        "other": 30,
    }

    # Mapeo de motivos a tratamientos
    REASON_MAPPING = {
        "limpieza": ("cleaning", 15),
        "extraccion": ("extraction", 30),
        "dolor": ("consultation", 15),
        "caries": ("caries", 30),
        "empaste": ("obturation", 30),
        "endodoncia": ("endodontics", 60),
        "conducto": ("endodontics", 60),
        "corona": ("crown", 45),
        "implante": ("implant", 90),
        "protesis": ("prosthesis", 30),
        "ortodoncia": ("orthodontics", 30),
        "brackets": ("orthodontics", 30),
        "blanqueamiento": ("whitening", 45),
        "consulta": ("consultation", 15),
        "primera": ("consultation", 15),
        "revision": ("consultation", 15),
    }

    def __init__(self, db: Session):
        self.db = db

    def classify_reason(self, reason: str) -> tuple:
        """Clasifica el motivo de consulta y retorna (tipo, duracion)"""
        reason_lower = reason.lower()

        for keyword, (treatment_type, duration) in self.REASON_MAPPING.items():
            if keyword in reason_lower:
                return treatment_type, duration

        return "consultation", 15  # Default

    def get_professional_for_treatment(
        self, treatment_type: str
    ) -> Optional[Professional]:
        """Obtiene el profesional más adecuado según el tipo de tratamiento"""

        # Mapeo de especialidades
        SPECIALTY_MAPPING = {
            "extraction": ["Cirugía", "Extracciones", "General"],
            "implant": ["Implantología", "Cirugía", "General"],
            "prosthesis": ["Prótesis", "General"],
            "endodontics": ["Endodoncia", "Conductos", "General"],
            "orthodontics": ["Ortodoncia", "Brackets"],
            "crown": ["Prótesis", "General"],
            "obturation": ["General", "Restauraciones"],
            "cleaning": ["General", "Higiene"],
            "consultation": ["General"],
        }

        specialties = SPECIALTY_MAPPING.get(treatment_type, ["General"])

        # Buscar profesional con especialidad adecuada
        for specialty in specialties:
            prof = (
                self.db.query(Professional)
                .filter(
                    Professional.specialty.ilike(f"%{specialty}%"),
                    Professional.is_active == True,
                )
                .first()
            )
            if prof:
                return prof

        # Fallback: primer profesional activo
        return (
            self.db.query(Professional).filter(Professional.is_active == True).first()
        )

    def get_available_slots(
        self,
        professional_id: int,
        treatment_duration: int,
        days_ahead: int = 14,
        start_from: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene slots disponibles para un profesional considerando:
        - Sus horarios de disponibilidad
        - Turnos existentes
        - Duración del tratamiento
        """
        if start_from is None:
            start_from = datetime.now()

        end_date = start_from + timedelta(days=days_ahead)

        # Obtener disponibilidad del profesional
        availabilities = (
            self.db.query(Availability)
            .filter(Availability.professional_id == professional_id)
            .all()
        )

        if not availabilities:
            return []

        # Obtener turnos existentes del profesional en el rango
        existing_appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.professional_id == professional_id,
                Appointment.start_at >= start_from,
                Appointment.start_at <= end_date,
                Appointment.status.in_(["confirmed", "pending"]),
            )
            .order_by(Appointment.start_at)
            .all()
        )

        # Crear mapa de ocupación por día
        occupied_slots = {}
        for apt in existing_appointments:
            day_key = apt.start_at.date()
            if day_key not in occupied_slots:
                occupied_slots[day_key] = []
            occupied_slots[day_key].append({"start": apt.start_at, "end": apt.end_at})

        available_slots = []
        current_date = start_from.date()

        while current_date <= end_date.date():
            # Obtener disponibilidad para este día de la semana
            day_of_week = current_date.isoweekday()  # 1=Lunes, 7=Domingo
            day_availability = [
                a for a in availabilities if a.day_of_week == day_of_week
            ]

            if not day_availability:
                current_date += timedelta(days=1)
                continue

            # Generar slots para cada rango de disponibilidad del día
            for avail in day_availability:
                slots = self._generate_slots_for_day(
                    current_date,
                    avail.start_time,
                    avail.end_time,
                    avail.slot_minutes or 30,
                    treatment_duration,
                    occupied_slots.get(current_date, []),
                )
                available_slots.extend(slots)

            current_date += timedelta(days=1)

        return available_slots

    def _generate_slots_for_day(
        self,
        date: datetime.date,
        start_time: time,
        end_time: time,
        slot_interval: int,
        treatment_duration: int,
        occupied: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Genera slots disponibles para un día específico"""

        slots = []
        current_time = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)

        while current_time + timedelta(minutes=treatment_duration) <= end_datetime:
            slot_end = current_time + timedelta(minutes=treatment_duration)

            # Verificar si el slot está disponible (no colisiona con turnos existentes)
            is_available = True
            for apt in occupied:
                if current_time < apt["end"] and slot_end > apt["start"]:
                    is_available = False
                    break

            if is_available:
                slots.append(
                    {
                        "start": current_time,
                        "end": slot_end,
                        "duration": treatment_duration,
                    }
                )

            current_time += timedelta(minutes=slot_interval)

        return slots

    def find_available_slots(
        self, reason: str, days_ahead: int = 14, max_options: int = 6
    ) -> Dict[str, Any]:
        """
        Busca slots disponibles para un motivo de consulta
        Retorna información del profesional asignado y opciones de horarios
        """
        # Clasificar el tratamiento
        treatment_type, duration = self.classify_reason(reason)

        # Obtener profesional
        professional = self.get_professional_for_treatment(treatment_type)

        if not professional:
            return {
                "success": False,
                "error": "No hay profesionales disponibles",
                "treatment_type": treatment_type,
                "duration": duration,
            }

        # Buscar slots disponibles
        slots = self.get_available_slots(
            professional_id=professional.id,
            treatment_duration=duration,
            days_ahead=days_ahead,
        )

        # Limitar opciones
        slots = slots[:max_options]

        # Formatear respuesta
        return {
            "success": True,
            "professional": {
                "id": professional.id,
                "name": professional.full_name,
                "specialty": professional.specialty,
            },
            "treatment": {
                "type": treatment_type,
                "duration": duration,
                "reason": reason,
            },
            "slots": [
                {
                    "datetime": slot["start"].isoformat(),
                    "date": slot["start"].strftime("%A %d/%m"),
                    "time": slot["start"].strftime("%H:%M"),
                    "end_time": slot["end"].strftime("%H:%M"),
                    "duration": slot["duration"],
                }
                for slot in slots
            ],
        }

    def book_appointment(
        self,
        patient_id: int,
        professional_id: int,
        start_datetime: datetime,
        reason: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Crea un turno en la base de datos"""

        treatment_type, duration = self.classify_reason(reason)
        end_datetime = start_datetime + timedelta(minutes=duration)

        # Verificar disponibilidad
        existing = (
            self.db.query(Appointment)
            .filter(
                Appointment.professional_id == professional_id,
                Appointment.start_at < end_datetime,
                Appointment.end_at > start_datetime,
                Appointment.status.in_(["confirmed", "pending"]),
            )
            .first()
        )

        if existing:
            return {"success": False, "error": "El horario ya no está disponible"}

        # Crear turno
        appointment = Appointment(
            patient_id=patient_id,
            professional_id=professional_id,
            start_at=start_datetime,
            end_at=end_datetime,
            reason=reason,
            notes=notes,
            status="confirmed",
        )

        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)

        return {
            "success": True,
            "appointment": {
                "id": appointment.id,
                "datetime": start_datetime.isoformat(),
                "date": start_datetime.strftime("%d/%m/%Y"),
                "time": start_datetime.strftime("%H:%M"),
                "duration": duration,
                "professional": appointment.professional.full_name
                if appointment.professional
                else None,
            },
        }

    def get_professional_schedule(
        self, professional_id: int, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Obtiene la agenda completa de un profesional en un rango de fechas"""

        appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.professional_id == professional_id,
                Appointment.start_at >= start_date,
                Appointment.start_at <= end_date,
            )
            .order_by(Appointment.start_at)
            .all()
        )

        return [
            {
                "id": apt.id,
                "start": apt.start_at.isoformat(),
                "end": apt.end_at.isoformat() if apt.end_at else None,
                "patient": f"{apt.patient.first_name} {apt.patient.last_name}"
                if apt.patient
                else None,
                "reason": apt.reason,
                "status": apt.status,
                "duration": (apt.end_at - apt.start_at).total_seconds() // 60
                if apt.end_at
                else None,
            }
            for apt in appointments
        ]


# Instancia global del servicio
def get_availability_service(db: Session) -> AvailabilityService:
    return AvailabilityService(db)
