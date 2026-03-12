"""
Sistema de Recordatorios Automáticos - Dental Studio Pro
Envía recordatorios de turnos por WhatsApp y Email
Se ejecuta periódicamente (recomendado: 1-2 veces al día)
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Appointment, Patient
from app.services.evolution import evolution_service
from app.services.email import email_service


class ReminderService:
    """Servicio para gestionar recordatorios de turnos"""

    def __init__(self, db: Session):
        self.db = db

    def get_upcoming_appointments(self, days_ahead: int = 1) -> List[Appointment]:
        """
        Obtiene turnos para los próximos días que necesitan recordatorio
        """
        target_date = datetime.now() + timedelta(days=days_ahead)
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.start_at >= start_of_day,
                Appointment.start_at <= end_of_day,
                Appointment.status.in_(["confirmed", "pending"]),
                Appointment.reminder_sent
                == False,  # Solo los que no han recibido recordatorio
            )
            .all()
        )

        return appointments

    def send_whatsapp_reminder(self, appointment: Appointment) -> bool:
        """Envía recordatorio por WhatsApp usando Evolution API"""
        try:
            patient = appointment.patient
            if not patient or not patient.phone:
                return False

            # Formatear mensaje
            date_str = appointment.start_at.strftime("%d/%m/%Y")
            time_str = appointment.start_at.strftime("%H:%M")

            message = (
                f"👋 *Hola {patient.first_name}!*\n\n"
                f"📅 Te recordamos que tienes un turno agendado para mañana:\n\n"
                f"📆 *Fecha:* {date_str}\n"
                f"⏰ *Hora:* {time_str}\n"
                f"🦷 *Motivo:* {appointment.reason or 'Consulta'}\n"
                f"👨‍⚕️ *Profesional:* {appointment.professional.full_name if appointment.professional else 'A confirmar'}\n\n"
                f"📍 *Dirección:* [Tu dirección]\n\n"
                f"*Por favor confirma tu asistencia respondiendo:*\n"
                f"✅ *SI* - Confirmo asistencia\n"
                f"❌ *NO* - Necesito cancelar/reprogramar\n\n"
                f"_Dental Studio Pro_ 🦷"
            )

            # Enviar mensaje
            evolution_service.send_message(patient.phone, message)

            # Marcar como enviado
            appointment.reminder_sent = True
            appointment.reminder_sent_at = datetime.now()
            self.db.commit()

            return True

        except Exception as e:
            print(
                f"Error sending WhatsApp reminder for appointment {appointment.id}: {e}"
            )
            return False

    def send_email_reminder(self, appointment: Appointment) -> bool:
        """Envía recordatorio por Email"""
        try:
            patient = appointment.patient
            if not patient or not patient.email:
                return False

            date_str = appointment.start_at.strftime("%d/%m/%Y")
            time_str = appointment.start_at.strftime("%H:%M")

            subject = f"Recordatorio de Turno - Dental Studio Pro - {date_str}"

            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #1e4d8c;">¡Hola {patient.first_name}!</h2>
                    
                    <p>Te recordamos que tienes un turno agendado para mañana:</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>📆 Fecha:</strong> {date_str}</p>
                        <p><strong>⏰ Hora:</strong> {time_str}</p>
                        <p><strong>🦷 Motivo:</strong> {appointment.reason or "Consulta"}</p>
                        <p><strong>👨‍⚕️ Profesional:</strong> {appointment.professional.full_name if appointment.professional else "A confirmar"}</p>
                    </div>
                    
                    <p><strong>📍 Dirección:</strong><br>
                    [Tu dirección]</p>
                    
                    <p style="background: #fff3cd; padding: 10px; border-radius: 5px;">
                        <strong>Importante:</strong> Si necesitas cancelar o reprogramar tu turno, 
                        por favor contáctanos con al menos 24 horas de anticipación.
                    </p>
                    
                    <p>¡Te esperamos!</p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 0.9em; color: #666;">
                        <strong>Dental Studio Pro</strong><br>
                        🦷 Tu salud dental es nuestra prioridad
                    </p>
                </div>
            </body>
            </html>
            """

            email_service.send_email(patient.email, subject, body)

            # Marcar como enviado
            appointment.reminder_sent = True
            appointment.reminder_sent_at = datetime.now()
            self.db.commit()

            return True

        except Exception as e:
            print(f"Error sending email reminder for appointment {appointment.id}: {e}")
            return False

    def process_reminders(self, days_ahead: int = 1) -> Dict[str, Any]:
        """
        Procesa todos los recordatorios pendientes
        """
        appointments = self.get_upcoming_appointments(days_ahead)

        results = {
            "total": len(appointments),
            "sent_whatsapp": 0,
            "sent_email": 0,
            "failed": 0,
            "appointments": [],
        }

        for appointment in appointments:
            patient = appointment.patient
            if not patient:
                continue

            sent = False

            # Intentar WhatsApp primero
            if patient.phone:
                if self.send_whatsapp_reminder(appointment):
                    results["sent_whatsapp"] += 1
                    sent = True

            # Si no se envió por WhatsApp, intentar Email
            if not sent and patient.email:
                if self.send_email_reminder(appointment):
                    results["sent_email"] += 1
                    sent = True

            if not sent:
                results["failed"] += 1

            results["appointments"].append(
                {
                    "id": appointment.id,
                    "patient": f"{patient.first_name} {patient.last_name}",
                    "date": appointment.start_at.isoformat(),
                    "sent": sent,
                }
            )

        return results


def run_reminders():
    """Función principal para ejecutar recordatorios (puede ser llamada por cron)"""
    db = SessionLocal()
    try:
        print(f"[{datetime.now()}] Iniciando proceso de recordatorios...")

        service = ReminderService(db)

        # Recordatorios para mañana
        results_tomorrow = service.process_reminders(days_ahead=1)
        print(f"Recordatorios para mañana: {results_tomorrow}")

        # Recordatorios para pasado mañana (opcional)
        # results_day_after = service.process_reminders(days_ahead=2)
        # print(f"Recordatorios para pasado mañana: {results_day_after}")

        print(f"[{datetime.now()}] Proceso completado.")

    except Exception as e:
        print(f"Error en proceso de recordatorios: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_reminders()
