# handlers/editor_handler.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from states import StudyPilotStates
from database import AsyncSessionLocal, Question
from sqlalchemy import select
import json

router = Router()

async def get_question_editor_markup(question_id: int) -> InlineKeyboardMarkup:
    """Savolni tahrirlash uchun inline tugmalar jamlanmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Savolni o'zgartirish", callback_data=f"edit_qtext_{question_id}"),
            InlineKeyboardButton(text="🔄 To'g'ri javobni o'zgartirish", callback_data=f"edit_qcor_{question_id}")
        ],
        [
            InlineKeyboardButton(text="➕ Variant qo'shish", callback_data=f"add_opt_{question_id}"),
            InlineKeyboardButton(text="🗑️ Savolni o'chirish", callback_data=f"del_q_{question_id}")
        ],
        [InlineKeyboardButton(text="⬅️ Bo'limga qaytish", callback_data="back_to_chunk")]
    ])

@router.callback_query(F.data.startswith("view_q_"))
async def view_question_for_editing(callback: CallbackQuery, state: FSMContext):
    """Savolni tahrirlash rejimida ko'rsatish"""
    question_id = int(callback.data.split("_")[2])
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Question).where(Question.id == question_id))
        question = result.scalar_one_or_none()
        
        if not question:
            await callback.answer("Savol topilmadi!", show_alert=True)
            return
            
        options = json.loads(question.options)
        options_text = "\n".join([f"{k}) {v}" for k, v in options.items()])
        
        text = (
            f"📝 **Savol tahrirlash paneli**\n\n"
            f"**Savol:** {question.question_text}\n\n"
            f"**Variantlar:**\n{options_text}\n\n"
            f"🎯 **To'g'ri javob:** {question.correct_option or 'Belgilanmagan'}"
        )
        
        markup = await get_question_editor_markup(question_id)
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data.startswith("edit_qcor_"))
async def edit_correct_answer_trigger(callback: CallbackQuery, state: FSMContext):
    """To'g'ri javob harfini o'zgartirishni boshlash"""
    question_id = callback.data.split("_")[2]
    await state.update_data(editing_question_id=question_id)
    
    await callback.message.answer("🎯 Ushbu savol uchun yangi to'g'ri javob harfini yuboring (Masalan: A yoki B):")
    await state.set_state(StudyPilotStates.editing_question)

@router.message(F.text, StudyPilotStates.editing_question)
async def save_edited_correct_answer(message: Message, state: FSMContext):
    """Yangi to'g'ri javobni bazaga saqlash"""
    new_correct = message.text.upper().strip()
    
    if len(new_correct) != 1 or new_correct not in ['A', 'B', 'C', 'D', 'E']:
        await message.answer("❌ Noto'g'ri format. Faqat bitta harf kiriting (A, B, C, D):")
        return
        
    data = await state.get_data()
    question_id = int(data.get("editing_question_id"))
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Question).where(Question.id == question_id))
        question = result.scalar_one_or_none()
        
        if question:
            question.correct_option = new_correct
            await session.commit()
            await message.answer(f"✅ {question_id}-savolning to'g'ri javobi [{new_correct}] ga muvaffaqiyatli o'zgartirildi!")
            
    await state.set_state(StudyPilotStates.main_menu)
                                              
