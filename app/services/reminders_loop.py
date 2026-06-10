import asyncio
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Appointment
from app.services.evolution import evolution_service
from config import settings

async def check_and_send_reminders():
    """Background task que revisa turnos próximos y envía recordatorios"""
    print("⏰ Tarea de recordatorios iniciada.")
    while True:
        try:
            db = SessionLocal()
            now = datetime.now()
            # Buscar turnos que sucedan en las próximas `reminder_hours` horas
            target_time = now + timedelta(hours=settings.reminder_hours)
            
            # Margen de 1 hora para no enviar muy anticipadamente si el bot se reinicia
            start_window = target_time - timedelta(minutes=30)
            end_window = target_time + timedelta(minutes=30)

            upcoming_appts = db.query(Appointment).filter(
                Appointment.start_at >= start_window,
                Appointment.start_at <= end_window,
                Appointment.status == "confirmed",
                Appointment.reminder_sent == False
            ).all()

            for appt in upcoming_appts:
                if not appt.patient or not appt.patient.phone:
                    continue

                cancel_url = f"{settings.public_url}/turnos/{appt.id}/cancelar"
                date_str = appt.start_at.strftime("%d/%m/%Y")
                time_str = appt.start_at.strftime("%H:%M")
                
                message = (
                    f"👋 *Hola {appt.patient.first_name}!* Te escribimos de Dental Studio Pro para recordarte "
                    f"tu turno agendado:\n\n"
                    f"📅 Fecha: {date_str}\n"
                    f"⏰ Hora: {time_str}\n"
                    f"🦷 Motivo: {appt.reason}\n\n"
                    f"❌ Si no puedes asistir, por favor cancela tu turno tocando el siguiente enlace:\n"
                    f"{cancel_url}\n\n"
                    f"¡Te esperamos!"
                )
                
                # Enviar WhatsApp
                success = await evolution_service.send_text(appt.patient.phone, message)
                
                if success:
                    appt.reminder_sent = True
                    appt.reminder_sent_at = datetime.now()
                    appt.reminder_channel = "whatsapp"
                    print(f"✅ Recordatorio enviado a {appt.patient.first_name} ({appt.patient.phone})")
                
            db.commit()
            db.close()

        except Exception as e:
            print(f"Error en tarea de recordatorios: {e}")
        
        # Dormir 15 minutos antes de la próxima revisión
        await asyncio.sleep(15 * 60)
