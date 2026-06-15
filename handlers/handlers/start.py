from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.future import select
from database import AsyncSessionLocal, User

router = Router()

def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📁 Mening Papkalarim")
    builder.button(text="📝 Kunlik Vazifa")
    builder.button(text="🔄 Aqlli Takrorlash")
    builder.button(text="⚔️ Quiz Battle")
    builder.button(text="📊 Xatolar Banki")
    builder.button(text="🔍 Qidiruv")
    builder.button(text="🔗 Do'stlarni taklif qilish")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username or "Foydalanuvchi"
    
    # Kelgan komandadan referral kodni ajratib olish (start=ref_12345)
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
        except ValueError:
            pass

    async with AsyncSessionLocal() as session:
        async with session.begin():
            # O'zini tekshirish
            result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
            user = result.scalars().first()
            
            if not user:
                # Yangi foydalanuvchi yaratish
                user = User(telegram_id=telegram_id, level="Beginner", xp=0)
                session.add(user)
                
                # Agar referral orqali kirgan bo'lsa va o'zini o'zi taklif qilmagan bo'lsa
                if referrer_id and referrer_id != telegram_id:
                    ref_result = await session.execute(select(User).filter_by(telegram_id=referrer_id))
                    referrer = ref_result.scalars().first()
                    if referrer:
                        referrer.xp += 100  # Taklif qilganga 100 XP
                        try:
                            await message.bot.send_message(
                                chat_id=referrer_id, 
                                text=f"🎉 Do'stingiz @{username} botga qo'shildi! Sizga +100 XP berildi."
                            )
                        except Exception:
                            pass
                            
                await session.commit()
                text = f"🚀 **Quiz AI** platformasiga xush kelibsiz, {username}!\n\nBu yerda siz o'quv materiallari, PDF va matnlarni yuklab, ulardan AI yordamida testlar, flashcardlar yaratishingiz mumkin."
            else:
                text = f"👋 Qayta tashrifingiz bilan, {username}!\n\nBugun qaysi material ustida ishlaymiz? Quyidagi menyudan kerakli bo'limni tanlang:"
                
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
  
