from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings


bot = Bot(token=settings.telegram_bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


async def setup_bot():
    """Configura el bot y registra los handlers"""
    from app.handlers.conversation import router
    try:
        dp.include_router(router)
    except ValueError:
        pass # Ignorar si el router ya está acoplado
    return dp

async def start_bot_polling():
    """Inicia el polling del bot en segundo plano"""
    await setup_bot()
    print(f"🧹 Cleaning old Telegram webhooks (Token ends in: ...{settings.telegram_bot_token[-4:] if settings.telegram_bot_token else 'NONE'})...")
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 Bot de Telegram iniciado mediante Polling...")
    try:
        await dp.start_polling(bot, handle_signals=False)
    except Exception as e:
        print(f"❌ Error en Polling de Telegram: {e}")

async def start_bot():
    """Wrapper para iniciar el bot (usado en threads si es necesario)"""
    await start_bot_polling()
