from aiogram import Bot
from aiogram.types import Message
from config import settings


class TelegramService:
    """Servicio para enviar mensajes por Telegram"""

    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token)

    async def send_message(self, chat_id: int, text: str) -> bool:
        """Envía un mensaje de texto"""
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
            return True
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    async def send_buttons(self, chat_id: int, text: str, buttons: list) -> bool:
        """Envía mensaje con botones inline"""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        try:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=btn, callback_data=f"btn_{i}")]
                    for i, btn in enumerate(buttons)
                ]
            )
            await self.bot.send_message(
                chat_id=chat_id, text=text, reply_markup=keyboard
            )
            return True
        except Exception as e:
            print(f"Error sending buttons: {e}")
            return False

    async def send_html(self, chat_id: int, html: str) -> bool:
        """Envía mensaje con formato HTML"""
        try:
            await self.bot.send_message(chat_id=chat_id, text=html, parse_mode="HTML")
            return True
        except Exception as e:
            print(f"Error sending HTML: {e}")
            return False


telegram_service = TelegramService()
