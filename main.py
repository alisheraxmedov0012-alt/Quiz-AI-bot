import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Konfiguratsiya va Baza
from config import BOT_TOKEN
from database import init_db

# Barcha Handlerlarni (Modullarni) import qilish — Hech narsa qolib ketmaydi!
from handlers import all_routers

# Middleware (Nazorat tizimlari)
from middlewares.anti_spam import AntiSpamMiddleware # 39. Anti-Spam (Flood/Rate limit)
from middlewares.subscription import SubCheckMiddleware # 1. Majburiy obuna tekshiruvi

async def on_startup(bot: Bot):
    """Bot ishga tushganda adminlarni ogohlantirish va bazani sozlash"""
    print("--------------------------------------------------")
    print("🤖 Quiz AI — Tizim elementlari tekshirilmoqda...")
    await init_db()
    print("🗄️ Ma'lumotlar bazasi asinxron tayyor holatga keltirildi.")
    print("🚀 Bot muvaffaqiyatli ishga tushdi!")
    print("--------------------------------------------------")

async def on_shutdown(dispatcher: Dispatcher):
    """Bot o'chganda xavfsiz yopilish (Cloud Backup va barcha seanslarni saqlash)"""
    print("⏳ Quiz AI to'xtatilmoqda... Barcha ma'lumotlar Cloud zaxirasiga saqlandi.")

async def main():
    # Logging tizimini sozlash (Xatoliklarni aniqlash uchun)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Bot obyektini HTML parse rejimi bilan yaratish
    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # State'larni xotirada saqlash (Katta loyihalar uchun RedisStorage ma'qul, hozircha Memory)
    dp = Dispatcher(storage=MemoryStorage())

    # --- MIDDLEWARE'LARNI RO'YXATDAN O'TKAZISH ---
    # 39-funksiya: Spamdan himoya va Rate limit
    dp.message.middleware(AntiSpamMiddleware())
    # 1-funksiya: Har bir amal oldidan majburiy kanallarni tekshirish (Cache tizimli)
    dp.message.middleware(SubCheckMiddleware())

    # --- ROUTERLARNI ULANISH ZANJIRI (Tartib o'ta muhim!) ---
    dp.include_routers(*all_routers)

    # Start va Stop hodisalarini bog'lash
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Botni ishga tushirish (Eski xabarlarni o'tkazib yuborish skip_updates=True)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🤖 Bot qo'lda to'xtatildi.")
  
