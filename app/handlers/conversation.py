import json
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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


def get_session(db: Session, chat_id: str) -> ChatSession:
    """Obtiene o crea una sesión de chat"""
    session = db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first()
    if not session:
        session = ChatSession(
            chat_id=chat_id, channel="telegram", step="start", payload="{}"
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
        if payload:
            session.payload = json.dumps(payload)
        if patient_id:
            session.patient_id = patient_id
        db.commit()


async def send_response(chat_id: str, channel: str, text: str):
    """Envía respuesta por el canal apropiado"""
    if channel == "telegram":
        await telegram_service.send_message(int(chat_id), text)
    elif channel == "whatsapp":
        number = chat_id.replace("@c.us", "").replace("@g.us", "")
        evolution_service.send_text(number, text)


def get_available_slots(days_ahead: int = 14, max_slots: int = 5) -> list:
    """Genera horarios disponibles (simulado)"""
    slots = []
    now = datetime.now()

    # Generar slots de ejemplo (lunes a viernes, 9 a 17hs)
    for d in range(1, days_ahead + 1):
        day = now + timedelta(days=d)
        if day.weekday() < 5:  # Lunes a viernes
            for hour in range(9, 17):
                slot_time = day.replace(hour=hour, minute=0, second=0, microsecond=0)
                if slot_time > now:
                    slots.append(
                        {
                            "datetime": slot_time,
                            "display": slot_time.strftime("%d/%m a las %H:%M"),
                        }
                    )
                    if len(slots) >= max_slots:
                        return slots
    return slots


# ==================== HANDLERS ====================


@router.message(F.text == "/start")
async def cmd_start(message: Message, db: Session = SessionLocal()):
    """Comando /start - Inicia la conversación"""
    chat_id = str(message.chat.id)

    session = get_session(db, chat_id)
    session.channel = "telegram"
    db.commit()

    welcome_text = """🦷 *Bienvenido a Clínica Odontológica*

Soy el asistente de turnos. Puedo ayudarte a:

📅 *Solicitar un turno*
❌ *Cancelar o reprogramar*
📋 *Ver información*

¿En qué puedo ayudarte hoy?"""

    await message.answer(welcome_text, parse_mode="Markdown")
    update_session(db, chat_id, "start")


@router.message(F.text.in_(["/help", "/ayuda"]))
async def cmd_help(message: Message, db: Session = SessionLocal()):
    """Comando de ayuda"""
    help_text = """📋 *Comandos disponibles:*

/start - Iniciar conversación
/turno - Solicitar turno
/cancelar - Cancelar turno
/ayuda - Ver esta ayuda

También puedes escribir naturalmente lo que necesites."""

    await message.answer(help_text, parse_mode="Markdown")


@router.message(F.text == "/turno")
async def cmd_turno(message: Message, db: Session = SessionLocal()):
    """Inicia el proceso de solicitud de turno"""
    chat_id = str(message.chat.id)

    welcome_text = """📅 *Solicitar Turno*

Perfecto, te ayudo a coordinar tu turno.

Por favor, dime tu *nombre completo* (ej: Juan Pérez)"""

    await message.answer(welcome_text, parse_mode="Markdown")
    update_session(db, chat_id, "ask_name")


@router.message()
async def handle_message(message: Message, db: Session = SessionLocal()):
    """Maneja todos los mensajes entrantes"""
    chat_id = str(message.chat.id)
    text = message.text or ""
    session = get_session(db, chat_id)

    step = session.step
    payload = json.loads(session.payload or "{}")

    # Flujo de conversación
    if step == "start":
        if any(
            word in text.lower() for word in ["turno", "sacar", "reservar", "pedir"]
        ):
            await cmd_turno(message, db)
        elif any(word in text.lower() for word in ["cancelar", "reprogramar"]):
            await cmd_cancelar(message, db)
        else:
            await cmd_start(message, db)

    elif step == "ask_name":
        # Guardar nombre y pedir obra social
        payload["name"] = text
        update_session(db, chat_id, "ask_obra", payload)

        await message.answer(
            "✅ Perfecto, {name}\n\n🏥 ¿Tienes obra social? Si es así, ¿cuál?".format(
                name=text
            ),
            parse_mode="Markdown",
        )

    elif step == "ask_obra":
        # Guardar obra social y pedir motivo
        payload["obra_social"] = text
        update_session(db, chat_id, "ask_reason", payload)

        await message.answer(
            "✅ Merci!\n\n"
            "🦷 ¿Cuál es el motivo de tu consulta?\n"
            "(ej: dolor de muela, limpieza, ortodoncia, etc.)"
        )

    elif step == "ask_reason":
        # Clasificar motivo y pedir teléfono
        category = classify_reason(text)
        payload["reason"] = text
        payload["category"] = category

        update_session(db, chat_id, "ask_phone", payload)

        emoji_map = {
            "ortodoncia": "🦷",
            "conductos": "🔴",
            "extracciones": "🔧",
            "implantes": "⚙️",
            "protesis": "🦋",
            "consulta": "💬",
        }
        emoji = emoji_map.get(category, "📅")

        await message.answer(
            f"{emoji} Entendido: *{text}*\n\n📱 ¿Cuál es tu número de teléfono?",
            parse_mode="Markdown",
        )

    elif step == "ask_phone":
        # Guardar teléfono y ofrecer horarios
        phone = normalize_ar_phone(text)
        payload["phone"] = phone

        # Crear o buscar paciente
        patient = get_or_create_patient(
            db,
            phone=phone,
            first_name=payload.get("name", "").split()[0],
            last_name=" ".join(payload.get("name", "").split()[1:]),
        )

        update_session(db, chat_id, "choose_slot", payload, patient.id)

        # Obtener horarios disponibles
        slots = get_available_slots()

        slots_text = "⏰ *Horarios disponibles:*\n\n"
        for i, slot in enumerate(slots, 1):
            slots_text += f"{i}. {slot['display']}\n"

        slots_text += "\nResponde con el *número* del horario que prefieras."

        await message.answer(slots_text, parse_mode="Markdown")

    elif step == "choose_slot":
        # Confirmar turno
        try:
            slot_index = int(text) - 1
            slots = get_available_slots()

            if 0 <= slot_index < len(slots):
                slot = slots[slot_index]
                patient_id = session.patient_id

                # Crear turno en la base de datos
                appointment = Appointment(
                    patient_id=patient_id,
                    professional_id=1,  # Por defecto el primero
                    reason=payload.get("reason", ""),
                    category=payload.get("category", "consulta"),
                    start_at=slot["datetime"],
                    end_at=slot["datetime"] + timedelta(minutes=30),
                    status="confirmed",
                    channel=session.channel,
                )
                db.add(appointment)
                db.commit()

                # Confirmar al paciente
                confirm_text = f"""✅ *Turno Confirmado*

📅 Fecha: {slot["display"]}
🦷 Motivo: {payload.get("reason", "Consulta")}
📱 Canal: {session.channel.title()}

💡 Recordatorio: Responde 'REPROGRAMAR' si necesitas cambiar.

ℹ️ Los mensajes son solo de texto."""

                await message.answer(confirm_text, parse_mode="Markdown")
                update_session(db, chat_id, "confirmed")
            else:
                await message.answer(
                    "❌ Número inválido. Por favor elegí un número de la lista."
                )
        except ValueError:
            await message.answer("❌ Por favor, respondé con el *número* del horario.")

    else:
        # Cualquier otro paso, reiniciar
        await cmd_start(message, db)


async def cmd_cancelar(message: Message, db: Session = SessionLocal()):
    """Maneja solicitud de cancelación"""
    chat_id = str(message.chat.id)

    # Buscar turnos confirmados del paciente
    session = get_session(db, chat_id)

    if session.patient_id:
        appointments = (
            db.query(Appointment)
            .filter(
                Appointment.patient_id == session.patient_id,
                Appointment.status == "confirmed",
            )
            .all()
        )

        if appointments:
            text = "❌ *Cancelar Turno*\n\nTus turnos:\n\n"
            for i, appt in enumerate(appointments, 1):
                text += f"{i}. {appt.start_at.strftime('%d/%m a las %H:%M')} - {appt.reason}\n"
            text += "\nresponde con el número del turno a cancelar."

            await message.answer(text, parse_mode="Markdown")
            update_session(db, chat_id, "cancel_select")
        else:
            await message.answer("No tienes turnos confirmados para cancelar.")
    else:
        await message.answer("No encontré tus datos. Iniciá con /start")


# ==================== WEBHOOK DE WHATSAPP ====================


async def handle_whatsapp_message(phone: str, text: str):
    """Maneja mensajes entrantes de WhatsApp via Evolution API"""
    db = SessionLocal()
    try:
        chat_id = f"{phone}@c.us"
        session = get_session(db, chat_id)
        session.channel = "whatsapp"
        db.commit()

        # Procesar mensaje similar a Telegram
        # (aquí se reutilizaría la lógica del handler)

        # Por ahora, iniciar flujo si es start
        if text.lower() in ["hola", "start", "iniciar"]:
            welcome_text = """🦷 *Bienvenido a Clínica Odontológica*

Soy el asistente de turnos. Escribe 'TURNO' para solicitar."""
            evolution_service.send_text(phone, welcome_text)
        elif text.upper() == "TURNO":
            await cmd_turno_whatsapp(db, chat_id, phone)

    finally:
        db.close()


async def cmd_turno_whatsapp(db: Session, chat_id: str, phone: str):
    """Inicia flujo de turno para WhatsApp"""
    update_session(db, chat_id, "ask_name")
    evolution_service.send_text(phone, "Por favor, dime tu nombre completo:")
