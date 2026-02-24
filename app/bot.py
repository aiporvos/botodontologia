from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings


bot = Bot(token=settings.telegram_bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


async def setup_bot():
    """Configura el bot y registra los handlers"""
    from app.handlers.conversation import router

    dp.include_router(router)

    return dp


async def start_bot():
    """Inicia el polling del bot"""
    from app.handlers.conversation import router

    dp.include_router(router)

    print("🤖 Bot de Telegram iniciado...")
    await dp.start_polling(bot)
