from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("daily"))
@router.message(F.text == "📝 Kunlik Vazifa")
async def show_daily_challenge(message: types.Message):
    # Bu yerda foydalanuvchining kunlik test rejasi hisoblanadi
    text = (
        "📅 **Bugungi Kunlik Vazifangiz:**\n\n"
        "1. AI yordamida yangi 1 ta PDF faylni tahlil qiling.\n"
        "2. Generatsiya qilingan testdan kamida 80% to'g'ri javob toping.\n\n"
        "🎁 **Mukofot:** `+150 XP` va `🔥 1 Kunlik Streak (Ketma-ketlik)`\n\n"
        "Sizning joriy uzluksiz o'qiyotgan kunlaringiz: 🔥 **0 kun**"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Vazifani boshlash", callback_data="start_daily_task")
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
  
