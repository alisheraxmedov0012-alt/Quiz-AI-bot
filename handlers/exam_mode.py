import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database import AsyncSessionLocal, Question
from sqlalchemy import select, func
import json

router = Router()

@router.callback_query(F.data.startswith("start_exam_"))
async def start_timed_exam(callback: CallbackQuery, state: FSMContext):
    """Vaqtli Imtihon (26-funksiya): 30 daqiqalik tasodifiy imtihon start oladi"""
    test_bank_id = int(callback.data.split("_")[2])
    
    async with AsyncSessionLocal() as session:
        # Bazadan tasodifiy 20 ta savolni olish (25-funksiya)
        result = await session.execute(
            select(Question).where(Question.test_bank_id == test_bank_id).order_by(func.random()).limit(20)
        )
        questions = result.scalars().all()
        
        exam_qs = [{"id": q.id, "q": q.question_text, "options": json.loads(q.options), "a": q.correct_option} for q in questions]
        
        await state.update_data(exam_questions=exam_qs, exam_index=0, exam_score=0)
        
        await callback.message.answer("⏱️ **Imtihon boshlandi!** Jami: 20 ta savol. Sizda 30 daqiqa vaqt bor.")
        
        # Orqa fonda taymerni ishga tushirish taski
        asyncio.create_task(exam_timer_task(callback.message.chat.id, state, 1800)) # 1800 soniya = 30 daqiqa
        await send_next_exam_question(callback, state)

async def exam_timer_task(chat_id: int, state: FSMContext, seconds: int):
    """Imtihon taymer vazifasi"""
    await asyncio.sleep(seconds)
    current_state = await state.get_state()
    # Agar foydalanuvchi hali ham imtihonda bo'lsa, avtomatik yopish
    if current_state: 
        print("Vaqt tugadi!")
        # Bu yerda vaqt tugaganligi haqida ogohlantirish va natijani chiqarish mantiqi bo'ladi

async def send_next_exam_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("exam_index")
    exam_qs = data.get("exam_questions")
    
    if index >= len(exam_qs):
        await callback.message.answer(f"🏁 **Imtihon yakunlandi!** Natijangiz: {data.get('exam_score')}/{len(exam_qs)}")
        return
        
    current_q = exam_qs[index]
    # Tugmalarni chiqarish va javobni tekshirish xuddi study_mode kabi amalga oshiriladi...

