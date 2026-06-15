from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("battle"))
@router.message(F.text == "⚔️ Quiz Battle")
async def start_quiz_battle(message: types.Message):
    text = (
        "⚔️ **Quiz AI — Jonli Bellashuv Arenasi (1v1)**\n\n"
        "Bu yerda siz tasodifiy raqib bilan yoki do'stingizni chaqirgan holda, "
        "ma'lum bir fan doirasida test yechish tezligi bo'yicha bellashasiz!\n\n"
        "🏆 G'olib bo'lgan ishtirokchi raqibidan **+50 XP** ball tortib oladi."
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Tasodifiy raqib qidirish", callback_data="battle_matchmaking")
    builder.button(text="👥 Do'stni jangga chaqirish", callback_data="battle_invite_friend")
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@router.callback_query(F.data == "battle_matchmaking")
async def process_matchmaking(callback: types.CallbackQuery):
    await callback.message.edit_text("🔍 Raqib qidirilmoqda... Iltimos, arenada kutib turing...")
    await callback.answer()
  
