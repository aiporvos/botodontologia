import json
import asyncio
from datetime import datetime, timedelta
from aiogram import Router
from aiogram.types import Message
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ChatSession, Patient, Appointment, Professional
from app.services.telegram import telegram_service
from app.services.evolution import evolution_service
from app.services.ai_agent import ai_agent

router = Router()

async def send_smart_response(chat_id: str, channel: str, text: str):
    """Procesa el texto con el Agente IA y envía la respuesta dividida"""
    response_text = await ai_agent.ask(chat_id, text)
    
    # Limpieza de caracteres técnicos (estilo n8n)
    clean_text = response_text.replace("*", "").replace("#", "").replace("¡", "").replace("¿", "")
    
    # División en burbujas de mensaje
    parts = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
    if not parts: parts = [clean_text]

    for part in parts[:3]: # Límite de 3 partes para no spamear
        if channel == "whatsapp":
            phone = chat_id.replace("@c.us", "")
            await evolution_service.send_text(phone, part)
        elif channel == "telegram":
            await telegram_service.send_message(int(chat_id), part)
        await asyncio.sleep(1.2)

# ==================== HANDLERS AIOGRAM (TELEGRAM) ====================

@router.message()
async def aiogram_handler(message: Message):
    """Handler para Telegram"""
    await send_smart_response(str(message.chat.id), "telegram", message.text or "")

# ==================== WHATSAPP ENTRY POINT ====================

async def handle_whatsapp_message(phone: str, text: str):
    """Handler para WhatsApp"""
    chat_id = f"{phone}@c.us"
    await send_smart_response(chat_id, "whatsapp", text)
