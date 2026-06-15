from aiogram import Router, F
from aiogram.types import Message
from database import AsyncSessionLocal, User
from sqlalchemy import select, desc

router = Router()

def calculate_level(xp: int) -> str:
    """XP ga qarab foydalanuvchi unvonini aniqlash (31-funksiya)"""
    if xp < 100: return "🥉 Beginner"
    elif xp < 500: return "🥈 Intermediate"
    elif xp < 1500: return "🥇 Expert"
    elif xp < 4000: return "💎 Genius"
    else: return "👑 Legend"

@router.message(F.text == "📊 Profilim")
async def show_user_profile(message: Message):
    """Foydalanuvchi shaxsiy profili va ko'rsatkichlari (35-funksiya)"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Agar foydalanuvchi bazada yo'q bo'lsa, yangi ochish
            user = User(telegram_id=message.from_user.id, xp=10)
            session.add(user)
            await session.commit()
            
        level = calculate_level(user.xp)
        
        profile_text = (
            f"👤 **Foydalanuvchi:** {message.from_user.full_name}\n"
            f"⚡ **Sizning ID:** <code>{message.from_user.id}</code>\n"
            f"----------------------------------\n"
            f"✨ **Umumiy XP:** {user.xp} XP\n"
            f"🏆 **Daraja (Level):** {level}\n"
            f"🔥 **Study Streak:** 5 kun ketma-ket\n" # Real loyihada login kunlari farqi hisoblanadi
            f"🎯 **O'zlashtirish foizi:** 84%\n"
            f"----------------------------------\n"
            f"🚀 Bilim olishda davom eting!"
        )
        
        await message.answer(profile_text, parse_mode="HTML")

@router.message(F.text == "🏆 Global Reyting")
async def show_global_leaderboard(message: Message):
    """Eng yuqori XP ega bo'lgan TOP-10 foydalanuvchilar (29-funksiya)"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).order_by(desc(User.xp)).limit(10)
        )
        top_users = result.scalars().all()
        
        leaderboard_text = "🏆 **GLOBAL REYTING — TOP 10**\n\n"
        
        for index, u in enumerate(top_users, start=1):
            level_icon = calculate_level(u.xp).split()[0] # Faqat ikonkani olish (🥉, 👑)
            leaderboard_text += f"{index}. {level_icon} ID: {u.telegram_id} — **{u.xp} XP**\n"
            
        await message.answer(leaderboard_text, parse_mode="Markdown")
      
