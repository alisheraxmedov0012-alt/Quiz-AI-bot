from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import StudyPilotStates
from database import AsyncSessionLocal, Folder, TestBank, Question
from parser import parse_raw_text_to_questions, ask_ai_to_parse_and_solve
import json

router = Router()

@router.message(F.text, StudyPilotStates.waiting_for_material)
async def handle_material_input(message: Message, state: FSMContext):
    """Foydalanuvchi matn yuborganda uni vaqtincha saqlab, papka tanlashni so'rash"""
    await state.update_data(raw_text=message.text)
    
    # Bazadan foydalanuvchining mavjud papkalarini olish
    async with AsyncSessionLocal() as session:
        # Bu yerda user_id bo'yicha papkalarni chiqaramiz (Hozircha test uchun dinamik tugma)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📁 IELTS", callback_data="folder_1")],
            [InlineKeyboardButton(text="📁 Matematika", callback_data="folder_2")],
            [InlineKeyboardButton(text="➕ Yangi papka ochish", callback_data="create_new_folder")]
        ])
        
    await message.answer("📂 Ushbu materialni qaysi papkaga joylashtiramiz?", reply_markup=keyboard)
    await state.set_state(StudyPilotStates.choosing_folder)

@router.callback_query(F.data.startswith("folder_"), StudyPilotStates.choosing_folder)
async def handle_folder_selection(callback: CallbackQuery, state: FSMContext):
    """Papka tanlangach, javob kalitlarini qanday aniqlashni so'rash"""
    folder_id = callback.data.split("_")[1]
    await state.update_data(selected_folder_id=folder_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 AI orqali aniqlash", callback_data="key_ai")],
        [InlineKeyboardButton(text="✍️ Manual kiritish (Plain text)", callback_data="key_manual")]
    ])
    
    await callback.message.edit_text("🔍 Savollar ajratildi! To'g'ri javob kalitlarini qanday kiritamiz?", reply_markup=keyboard)
    await state.set_state(StudyPilotStates.choosing_key_method)

@router.callback_query(F.data == "key_ai", StudyPilotStates.choosing_key_method)
async def handle_ai_key_detection(callback: CallbackQuery, state: FSMContext):
    """AI orqali testlarni va kalitlarni aniqlash bosqichi"""
    await callback.message.edit_text("⏳ AI matnni tahlil qilmoqda va to'g'ri javoblarni qidirmoqda, iltimos kuting...")
    
    data = await state.get_data()
    raw_text = data.get("raw_text")
    
    # AI parserni chaqiramiz
    ai_results = await ask_ai_to_parse_and_solve(raw_text)
    
    if not ai_results:
        # Agar AI muvaffaqiyatsiz bo'lsa, oddiy regexga o'tadi
        ai_results = parse_raw_text_to_questions(raw_text)
        
    await state.update_data(parsed_questions=ai_results)
    
    # Bo'limlarga (Chunking) ajratish so'rovi
    total_q = len(ai_results)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔢 10 tadan", callback_data="chunk_10")],
        [InlineKeyboardButton(text="🔢 25 tadan", callback_data="chunk_25")],
        [InlineKeyboardButton(text="🌐 Hammasi bitta", callback_data="chunk_all")],
        [InlineKeyboardButton(text="✏️ O'z simvolimni kiritish", callback_data="chunk_custom")]
    ])
    
    await callback.message.answer(f"📦 Jami {total_q} ta savol topildi! Yodlash uchun ularni nechtadan bo'limlarga bo'lamiz?", reply_markup=keyboard)
    await state.set_state(StudyPilotStates.choosing_chunk_size)

@router.callback_query(F.data.startswith("chunk_"), StudyPilotStates.choosing_chunk_size)
async def finalize_test_creation(callback: CallbackQuery, state: FSMContext):
    """Tanlangan bo'limlar asosida testlarni bazaga saqlash va jarayonni yakunlash"""
    chunk_type = callback.data.split("_")[1]
    data = await state.get_data()
    questions = data.get("parsed_questions", [])
    folder_id = data.get("selected_folder_id")
    
    total_questions = len(questions)
    
    # Bo'lim hajmini aniqlash
    if chunk_type == "10": chunk_size = 10
    elif chunk_type == "25": chunk_size = 25
    else: chunk_size = total_questions
    
    async with AsyncSessionLocal() as session:
        # 1. Yangi TestBank (Versiya bilan) yaratish
        new_bank = TestBank(folder_id=int(folder_id), title=f"Test_v1", version=1)
        session.add(new_bank)
        await session.flush() # ID olish uchun
        
        # 2. Savollarni bazaga yozish
        for q in questions:
            db_q = Question(
                test_bank_id=new_bank.id,
                question_text=q['question'],
                options=json.dumps(q['options']),
                correct_option=q.get('correct'),
                ai_confidence=q.get('confidence', 1.0)
            )
            session.add(db_q)
            
        await session.commit()
        
    # Bo'limlar sonini hisoblash
    chunks_count = (total_questions + chunk_size - 1) // chunk_size
    
    await callback.message.edit_text(
        f"✅ Muvaffaqiyatli saqlandi!\n\n"
        f"📂 Papka ID: {folder_id}\n"
        f"📊 Jami savollar: {total_questions} ta\n"
        f"📦 Bo'limlar soni: {chunks_count} ta papka ichida ajratildi.\n\n"
        f"Endi ushbu bo'limlarni istalgan vaqtda tahrirlashingiz yoki yodlashni boshlashingiz mumkin!"
    )
    await state.set_state(StudyPilotStates.main_menu)
                                    
