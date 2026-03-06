import json
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ChatSession, Patient, Appointment, Professional
from app.utils.phone import normalize_ar_phone, get_or_create_patient
from app.utils.classify import classify_reason
from app.services.telegram import telegram_service
from app.services.evolution import evolution_service
from app.services.cal_com import calcom_service


router = Router()

# ==================== UTILIDADES ====================

def get_session(db: Session, chat_id: str, channel: str = "telegram") -> ChatSession:
    """Obtiene o crea una sesión de chat"""
    session = db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first()
    if not session:
        session = ChatSession(
            chat_id=chat_id, channel=channel, step="start", payload="{}"
        )
        db.add(session)
        db.commit()
    return session

def update_session(
    db: Session, chat_id: str, step: str, payload: dict = None, patient_id: int = None
):
    """Actualiza la sesión de chat"""
    session = db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first()
    if session:
        session.step = step
        if payload is not None:
            session.payload = json.dumps(payload)
        if patient_id:
            session.patient_id = patient_id
        db.commit()

async def send_response(chat_id: str, channel: str, text: str):
    """Envía respuesta por el canal apropiado de forma asíncrona"""
    if channel == "telegram":
        await telegram_service.send_message(int(chat_id), text)
    elif channel == "whatsapp":
        number = chat_id.replace("@c.us", "").replace("@g.us", "")
        await evolution_service.send_text(number, text)

# ==================== LÓGICA DE NEGOCIO ====================

async def process_conversation(db: Session, chat_id: str, channel: str, text: str):
    """Corazón del bot: maneja la lógica de estados para cualquier canal"""
    session = get_session(db, chat_id, channel)
    step = session.step
    payload = json.loads(session.payload or "{}")
    text_clean = text.strip()

    # Comandos globales
    if text_clean.lower() in ["hola", "inicio", "start", "/start"]:
        welcome_text = (
            "🦷 *Bienvenido a Clínica Odontológica*\n\n"
            "Soy tu asistente virtual. Puedo ayudarte con:\n"
            "📅 *TURNO*: Para solicitar una cita\n"
            "❌ *CANCELAR*: Para anular un turno\n"
            "❓ *AYUDA*: Ver más opciones"
        )
        await send_response(chat_id, channel, welcome_text)
        update_session(db, chat_id, "start")
        return

    if step == "start":
        if any(word in text_clean.lower() for word in ["turno", "cita", "sacar", "pedir"]):
            await send_response(chat_id, channel, "📅 *Solicitar Turno*\n\nPor favor, dime tu *nombre completo*:")
            update_session(db, chat_id, "ask_name")
        elif any(word in text_clean.lower() for word in ["cancelar", "reprogramar"]):
            await handle_cancel_request(db, chat_id, channel, session)
        else:
            await send_response(chat_id, channel, "Escribe *TURNO* para agendar una cita o *CANCELAR* para ver tus turnos.")

    elif step == "ask_name":
        payload["name"] = text_clean
        update_session(db, chat_id, "ask_obra", payload)
        await send_response(chat_id, channel, f"✅ Gracias, {text_clean}.\n\n🏥 ¿Tienes obra social? (Si no tienes escribe 'Particular')")

    elif step == "ask_obra":
        payload["obra_social"] = text_clean
        update_session(db, chat_id, "ask_reason", payload)
        await send_response(chat_id, channel, "🦷 ¿Cuál es el motivo de tu consulta?\n(Limpieza, dolor, brackets, etc.)")

    elif step == "ask_reason":
        category = classify_reason(text_clean)
        payload["reason"] = text_clean
        payload["category"] = category
        update_session(db, chat_id, "ask_phone", payload)
        await send_response(chat_id, channel, "📱 Por último, dime tu *número de teléfono* con código de área (ej: 1122334455):")

    elif step == "ask_phone":
        phone = normalize_ar_phone(text_clean)
        payload["phone"] = phone
        
        # Buscar/Crear paciente
        patient = get_or_create_patient(
            db,
            phone=phone,
            first_name=payload.get("name", "").split()[0],
            last_name=" ".join(payload.get("name", "").split()[1:]),
            obra_social=payload.get("obra_social")
        )
        
        update_session(db, chat_id, "choose_slot", payload, patient.id)
        
        # Obtener disponibilidad real de Cal.com si hay tipos de eventos
        # Por ahora simulamos slots pero llamamos al servicio para estar listos
        start_search = datetime.now().isoformat()
        end_search = (datetime.now() + timedelta(days=7)).isoformat()
        
        # slots = await calcom_service.get_availability(settings.calcom_event_type_id, start_search, end_search)
        # fallback a slots simulados si no hay integración
        slots = [
            {"time": (datetime.now() + timedelta(days=1, hours=10)).replace(minute=0), "display": "Mañana a las 10:00"},
            {"time": (datetime.now() + timedelta(days=1, hours=11)).replace(minute=0), "display": "Mañana a las 11:00"},
            {"time": (datetime.now() + timedelta(days=2, hours=15)).replace(minute=0), "display": "Pasado mañana a las 15:00"},
        ]
        
        payload["available_slots"] = [{"time": s["time"].isoformat(), "display": s["display"]} for s in slots]
        update_session(db, chat_id, "choose_slot", payload)

        slots_text = "⏰ *Horarios disponibles:*\n\n"
        for i, s in enumerate(slots, 1):
            slots_text += f"{i}. {s['display']}\n"
        slots_text += "\nResponde con el *número* de la opción elegida."
        await send_response(chat_id, channel, slots_text)

    elif step == "choose_slot":
        try:
            idx = int(text_clean) - 1
            available = payload.get("available_slots", [])
            if 0 <= idx < len(available):
                selected = available[idx]
                dt = datetime.fromisoformat(selected["time"])
                
                # Crear turno
                appt = Appointment(
                    patient_id=session.patient_id,
                    professional_id=1,
                    reason=payload.get("reason", "Consulta"),
                    category=payload.get("category", "consulta"),
                    start_at=dt,
                    end_at=dt + timedelta(minutes=30),
                    status="confirmed",
                    channel=channel
                )
                db.add(appt)
                db.commit()
                
                await send_response(chat_id, channel, f"✅ *¡Turno Confirmado!*\n\n📅 Fecha: {selected['display']}\n📍 Dirección: Av. Principal 123\n\nTe esperamos.")
                update_session(db, chat_id, "start", {})
            else:
                await send_response(chat_id, channel, "❌ Opción inválida. Elige un número de la lista.")
        except Exception:
            await send_response(chat_id, channel, "❌ Por favor responde solo con el número de la opción.")

async def handle_cancel_request(db: Session, chat_id: str, channel: str, session: ChatSession):
    """Maneja la lista de turnos para cancelar"""
    if not session.patient_id:
        await send_response(chat_id, channel, "No tienes turnos registrados aún. Escribe TURNO para agendar.")
        return

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == session.patient_id,
        Appointment.status == "confirmed",
        Appointment.start_at >= datetime.now()
    ).all()

    if not appointments:
        await send_response(chat_id, channel, "No tienes turnos próximos confirmados.")
        update_session(db, chat_id, "start")
        return

    text = "❌ *Tus turnos próximos:*\n\n"
    for i, appt in enumerate(appointments, 1):
        text += f"{i}. {appt.start_at.strftime('%d/%m %H:%M')} - {appt.reason}\n"
    text += "\nEnvía el número para cancelar o 'SALIR'."
    
    await send_response(chat_id, channel, text)
    update_session(db, chat_id, "cancel_select")

# ==================== HANDLERS AIOGRAM ====================

@router.message()
async def aiogram_handler(message: Message):
    db = SessionLocal()
    try:
        await process_conversation(db, str(message.chat.id), "telegram", message.text or "")
    finally:
        db.close()

# ==================== WHATSAPP ENTRY POINT ====================

async def handle_whatsapp_message(phone: str, text: str):
    db = SessionLocal()
    try:
        chat_id = f"{phone}@c.us"
        await process_conversation(db, chat_id, "whatsapp", text)
    finally:
        db.close()
