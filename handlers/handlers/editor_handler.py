from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.future import select
from database import AsyncSessionLocal, TestBank, Question

router = Router()

@router.message(Command("edit_test"))
@router.message(F.text == "📝 Test Tahrirlash")
async def list_tests_for_edit(message: types.Message):
    async with AsyncSessionLocal() as session:
        # Foydalanuvchining oxirgi test banklarini olish
        result = await session.execute(select(TestBank).limit(10))
        tests = result.scalars().all()
        
        if not tests:
            await message.answer("Sizda hali yaratilgan testlar mavjud emas.")
            return
            
        builder = InlineKeyboardBuilder()
        for test in tests:
            builder.button(text=f"✏️ {test.title[:20]}...", callback_data=f"edit_bank_{test.id}")
        builder.adjust(1)
        
        await message.answer("Tahrirlamoqchi bo'lgan test blokini tanlang:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("edit_bank_"))
async def process_edit_bank(callback: types.CallbackQuery):
    bank_id = int(callback.data.split("_")[2])
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Question).filter_by(test_bank_id=bank_id))
        questions = result.scalars().all()
        
        if not questions:
            await callback.message.answer("Bu testda savollar topilmadi.")
            await callback.answer()
            return
            
        text = f"📊 **Test Savollari (ID: {bank_id}):**\n\n"
        builder = InlineKeyboardBuilder()
        
        for idx, q in enumerate(questions, 1):
            text += f"{idx}. {q.question_text[:40]}...\n"
            builder.button(text=f"Savol {idx} ni tahrirlash", callback_data=f"edit_q_{q.id}")
            
        builder.adjust(1)
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await callback.answer()
      
