from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db
from app.models import Patient, Appointment
from app.handlers.conversation import handle_whatsapp_message

router = APIRouter(tags=["webhooks"])

@router.post("/webhook")
async def webhook_evolution(request: Request):
    try:
        data = await request.json()
        print(f"📥 Received Webhook Evolution: {json.dumps(data, indent=2)}")
        messages = data.get("data", {}).get("messages", [])
        from app.services.multimedia import multimedia_service
        from app.services.evolution import evolution_service

        for msg in messages:
            if msg.get("key", {}).get("fromMe", False):
                continue

            msg_id = msg.get("key", {}).get("id")
            type = msg.get("type")
            from_num = msg.get("key", {}).get("remoteJid", "").split("@")[0]
            if not from_num:
                continue

            text = ""
            if type in ["conversation", "extendedTextMessage"]:
                text = msg.get("body", {}).get("text", {}).get("text", "") or msg.get(
                    "message", {}
                ).get("conversation", "")

            elif type == "audioMessage":
                b64 = await evolution_service.get_media_base64(msg_id)
                if b64:
                    text = await multimedia_service.transcribe_audio(b64)
                    print(f"🎙 Audio Transcribed: {text}")

            elif type == "imageMessage":
                b64 = await evolution_service.get_media_base64(msg_id)
                if b64:
                    desc = await multimedia_service.describe_image(b64)
                    text = f"[Imagen enviada por el paciente: {desc}]"
                    print(f"👁 Image Analyzed: {desc}")

            if text:
                await handle_whatsapp_message(from_num, text)

        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/webhook/calcom")
async def webhook_calcom(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        trigger_event = data.get("triggerEvent")
        payload = data.get("payload", {})

        if trigger_event == "BOOKING_CREATED":
            start = payload.get("startTime")
            end = payload.get("endTime")
            attendee = payload.get("attendees", [{}])[0]
            email = attendee.get("email")
            name = attendee.get("name")
            booking_id = str(payload.get("id"))

            patient = db.query(Patient).filter(Patient.email == email).first()
            if not patient:
                patient = Patient(
                    first_name=name.split()[0] if name else "Cal.com",
                    last_name=" ".join(name.split()[1:]) if name and " " in name else "User",
                    email=email,
                    phone=attendee.get("phoneNumber") or "0",
                    is_active=True,
                )
                db.add(patient)
                db.commit()
                db.refresh(patient)

            appt = Appointment(
                patient_id=patient.id,
                professional_id=1,
                start_at=datetime.fromisoformat(start.replace("Z", "+00:00")),
                end_at=datetime.fromisoformat(end.replace("Z", "+00:00")),
                reason=payload.get("title", "Cita Cal.com"),
                status="confirmed",
                channel="cal_com",
                calendar_event_id=booking_id,
            )
            db.add(appt)
            db.commit()

        return {"status": "ok"}
    except Exception as e:
        print(f"Error in Cal.com webhook: {e}")
        return {"status": "error"}

@router.post("/webhook/telegram")
async def webhook_telegram(request: Request):
    try:
        from app.bot import dp, bot
        from aiogram.types import Update

        update = Update(**await request.json())
        await dp.feed_update(bot=bot, update=update)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
