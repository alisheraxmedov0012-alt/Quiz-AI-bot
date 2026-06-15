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
from handlers import (
    start,             # 1. Start va Majburiy obuna (Cache tekshiruvi bilan)
    material_handler,  # 2-6. Material Import, AI Aniqlash va Bo'limlarga bo'lish
    editor_handler,    # 7-8. Test Editor va Version Control
    study_mode,        # 10-11. O'rganish rejimi (Repeat Until Master)
    error_bank,        # 12-13. Xatolar Banki va Faqat xatolarni ishlash
    repetition,        # 14. Smart Repetition (1, 3, 7, 14, 30 kunlik avto-qaytarish)
    bookmarks,         # 15-16. Bilish darajasi (Bilaman/Bilmayman) va Bookmark (Sevimlilar)
    search,            # 17. 1000+ savol ichidan qidiruv tizimi
    flashcards,        # 18-20. Flashcards, AI & Audio Flashcards (TTS)
    ai_features,       # 21-24. AI Summary, AI Teacher, AI Tutor va AI Tavsiyalar
    exam_mode,         # 25-26. Exam Mode va Vaqtli Imtihonlar (Timer)
    battle_mode,       # 27-28. Battle Mode (1vs1) va Multiplayer Quiz (2-50 kishi)
    gamification,      # 29-32. Reytinglar, XP Tizimi, Darajalar va Achievementlar
    daily_challenge,   # 33-35. Daily Challenge, Study Streak va Profil paneli
    referral,          # 36. Referral tizimi
    premium,           # 37. Premium obuna integratsiyasi
    admin_panel,       # 38, 40. Admin Panel (Broadcast, Statistika, Analytics)
)

# Middleware (Nazorat tizimlari)
from middlewares.anti_spam import AntiSpamMiddleware # 39. Anti-Spam (Flood/Rate limit)
from middlewares.subscription import SubCheckMiddleware # 1. Majburiy obuna tekshiruvi

async def on_startup(bot: Bot):
    """Bot ishga tushganda adminlarni ogohlantirish va bazani sozlash"""
    print("--------------------------------------------------")
    print("🤖 StudyPilot AI — Tizim elementlari tekshirilmoqda...")
    await init_db()
    print("🗄️ Ma'lumotlar bazasi asinxron tayyor holatga keltirildi.")
    print("🚀 Bot muvaffaqiyatli ishga tushdi!")
    print("--------------------------------------------------")

async def on_shutdown(dispatcher: Dispatcher):
    """Bot o'chganda xavfsiz yopilish (Cloud Backup va barcha seanslarni saqlash)"""
    print("⏳ StudyPilot AI to'xtatilmoqda... Barcha ma'lumotlar Cloud zaxirasiga saqlandi.")

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
    dp.include_routers(
        start.router,
        material_handler.router,
        editor_handler.router,
        study_mode.router,
        error_bank.router,
        repetition.router,
        bookmarks.router,
        search.router,
        flashcards.router,
        ai_features.router,
        exam_mode.router,
        battle_mode.router,
        gamification.router,
        daily_challenge.router,
        referral.router,
        premium.router,
        admin_panel.router
    )

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
  
