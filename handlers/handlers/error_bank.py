from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.future import select
from database import AsyncSessionLocal, Question

router = Router()

@router.message(Command("errors"))
@router.message(F.text == "📊 Xatolar Banki")
async def show_error_bank(message: types.Message):
    # Bu yerda AI ishonchi past bo'lgan yoki xato yechilgan savollar tahlil qilinadi
    async with AsyncSessionLocal() as session:
        # Namuna sifatida ai_confidence past yoki xato belgilangan savollarni filtrlaymiz
        result = await session.execute(select(Question).filter(Question.ai_confidence < 0.70).limit(5))
        wrong_questions = result.scalars().all()
        
        if not wrong_questions:
            await message.answer("🌟 **Ajoyib!** Xatolar bankingiz bo'sh. Siz barcha testlarni yuqori natija bilan yechgansiz!", parse_mode="Markdown")
            return
            
        text = "❌ **Siz xato qilgan yoki qiynalgan savollar ro'yxati:**\n\n"
        builder = InlineKeyboardBuilder()
        
        for idx, q in enumerate(wrong_questions, 1):
            text += f"❓ {idx}-savol: {q.question_text[:50]}...\n"
            builder.button(text=f"🔄 {idx}-savolni qayta yechish", callback_data=f"retry_q_{q.id}")
            
        builder.adjust(1)
        text += "\n*Tavsiya:* Bu savollarni qayta yechish orqali xatolaringizni mustahkamlab oling."
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
      
