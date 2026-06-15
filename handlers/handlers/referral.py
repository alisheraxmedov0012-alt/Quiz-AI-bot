from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()

@router.message(Command("invite"))
@router.message(F.text == "🔗 Do'stlarni taklif qilish")
async def generate_referral_link(message: types.Message):
    bot_info = await message.bot.get_me()
    bot_username = bot_info.username
    user_id = message.from_user.id
    
    # Har bir foydalanuvchi uchun unikal start_link tayyorlash
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    text = (
        "👥 **Do'stlarni taklif qilish tizimi**\n\n"
        "Botni do'stlaringizga ulashing! Har bir sizning havolangiz orqali ro'yxatdan o'tgan "
        "yangi foydalanuvchi uchun tizim sizga bonus taqdim etadi.\n\n"
        f"🎁 Mukofot: **+100 XP**\n\n"
        f"🔗 Sizning shaxsiy taklif havolangiz:\n`{referral_link}`"
    )
    
    await message.answer(text, parse_mode="Markdown")
  
