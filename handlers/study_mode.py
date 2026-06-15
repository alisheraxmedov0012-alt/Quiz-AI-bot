import json
import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import StudyPilotStates
from database import AsyncSessionLocal, Question, TestBank
from sqlalchemy import select

router = Router()

@router.callback_query(F.data.startswith("start_study_"))
async def start_study_session(callback: CallbackQuery, state: FSMContext):
    """O'rganish rejimini boshlash (Savollarni aralashtirib yuklash)"""
    test_bank_id = int(callback.data.split("_")[2])
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Question).where(Question.test_bank_id == test_bank_id)
        )
        questions = result.scalars().all()
        
        if not questions:
            await callback.answer("Bu bo'limda savollar topilmadi!", show_alert=True)
            return
            
        # Savollar ro'yxatini tuzish va aralashtirish (10-funksiya)
        q_list = []
        for q in questions:
            q_list.append({
                "id": q.id,
                "text": q.question_text,
                "options": json.loads(q.options),
                "correct": q.correct_option
            })
        
        random.shuffle(q_list) # Savollarni aralashtirish
        
        # FSM ma'lumotlariga saqlash
        await state.update_data(
            study_questions=q_list,
            current_q_index=0,
            wrong_questions=[], # Xatolar banki uchun vaqtincha ro'yxat
            master_mode=True
        )
        
        await send_next_study_question(callback, state)

async def send_next_study_question(callback: CallbackQuery, state: FSMContext):
    """Navbatdagi savolni variantlarini aralashtirib ko'rsatish"""
    data = await state.get_data()
    q_list = data.get("study_questions")
    index = data.get("current_q_index")
    
    if index >= len(q_list):
        # Repeat Until Master (11-funksiya) — Agar xatolar bo'lsa, ularni qaytadan boshlash
        wrong_qs = data.get("wrong_questions", [])
        if wrong_qs:
            await callback.message.answer(
                f"🔄 **Bo'lim tugadi.** Lekin sizda {len(wrong_qs)} ta xato bor.\n"
                f"**'Repeat Until Master'** rejimi ishga tushdi. Xatolaringiz ustida 0 bo'lguncha ishlaymiz!"
            )
            random.shuffle(wrong_qs)
            await state.update_data(study_questions=wrong_qs, current_q_index=0, wrong_questions=[])
            await send_next_study_question(callback, state)
        else:
            await callback.message.answer("🎉 Tabriklaymiz! Ushbu bo'limdagi barcha savollarni 0 ta xato bilan yopdingiz va Master darajasiga erishdingiz!")
            await state.set_state(StudyPilotStates.main_menu)
        return

    current_q = q_list[index]
    
    # Variantlarni aralashtirish (10-funksiya)
    options = list(current_q["options"].items())
    random.shuffle(options)
    
    buttons = []
    for letter, text in options:
        buttons.append([InlineKeyboardButton(text=f"{letter}) {text}", callback_data=f"ans_{letter}_{current_q['id']}")])
        
    # 15-funksiya: Bilish darajasi tugmalari va 16. Bookmark
    buttons.append([
        InlineKeyboardButton(text="🟢 Bilaman", callback_data=f"rate_good_{current_q['id']}"),
        InlineKeyboardButton(text="🔴 Bilmayman", callback_data=f"rate_bad_{current_q['id']}")
    ])
    buttons.append([InlineKeyboardButton(text="⭐ Sevimlilarga qo'shish (Bookmark)", callback_data=f"bookmark_{current_q['id']}")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(f"❓ **Savol {index+1}:** {current_q['text']}", reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data.startswith("ans_"))
async def check_study_answer(callback: CallbackQuery, state: FSMContext):
    """Foydalanuvchi javobini tekshirish va xatolarni eslab qolish"""
    _, chosen_letter, q_id = callback.data.split("_")
    data = await state.get_data()
    q_list = data.get("study_questions")
    index = data.get("current_q_index")
    current_q = q_list[index]
    
    if chosen_letter == current_q["correct"]:
        await callback.answer("✅ To'g'ri!", show_alert=False)
    else:
        await callback.answer(f"❌ Noto'g'ri! To'g'ri javob: {current_q['correct']}", show_alert=True)
        # Xatolar ro'yxatiga qo'shish (Repeat Until Master uchun)
        wrong_questions = data.get("wrong_questions", [])
        wrong_questions.append(current_q)
        await state.update_data(wrong_questions=wrong_questions)
        
        # 12-funksiya: Xatolar bankiga (Ma'lumotlar bazasiga) saqlash kodi shu yerga ulanadi
        
    # Keyingi savolga o'tish
    await state.update_data(current_q_index=index + 1)
    await send_next_study_question(callback, state)
  
