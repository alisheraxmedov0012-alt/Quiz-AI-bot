import json
import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database import AsyncSessionLocal, Question
from sqlalchemy import select
from gtts import gTTS

router = Router()

@router.callback_query(F.data.startswith("flash_start_"))
async def start_flashcard_session(callback: CallbackQuery, state: FSMContext):
    """Flashcard rejimini boshlash"""
    test_bank_id = int(callback.data.split("_")[2])
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Question).where(Question.test_bank_id == test_bank_id))
        questions = result.scalars().all()
        
        if not questions:
            await callback.answer("Bu bo'limda savollar topilmadi!", show_alert=True)
            return
            
        fc_list = [{"id": q.id, "q": q.question_text, "a": q.correct_option} for q in questions]
        
        await state.update_data(flashcards=fc_list, fc_index=0)
        await send_flashcard_front(callback, state)

async def send_flashcard_front(callback: CallbackQuery, state: FSMContext):
    """Flashcard'ning old tomonini (Savol) ko'rsatish (18-funksiya)"""
    data = await state.get_data()
    fc_list = data.get("flashcards")
    index = data.get("fc_index")
    
    if index >= len(fc_list):
        await callback.message.answer("🎉 Barcha flashcardlarni ko'rib chiqdingiz!")
        return
        
    current_fc = fc_list[index]
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Orqa tomonini ko'rish", callback_data=f"flash_flip_{current_fc['id']}")],
        [InlineKeyboardButton(text="🔊 Ovozli o'qish (TTS)", callback_data=f"flash_tts_{current_fc['id']}")]
    ])
    
    await callback.message.edit_text(
        f"🎴 **Flashcard #{index+1} (Old tomoni)**\n\n"
        f"❓ **Savol:** {current_fc['q']}",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("flash_flip_"))
async def flip_flashcard(callback: CallbackQuery, state: FSMContext):
    """Flashcard'ning orqa tomonini (Javob) ko'rsatish"""
    q_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    fc_list = data.get("flashcards")
    index = data.get("fc_index")
    current_fc = fc_list[index]
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Keyingi Flashcard", callback_data="flash_next")]
    ])
    
    await callback.message.edit_text(
        f"🎴 **Flashcard #{index+1} (Orqa tomoni)**\n\n"
        f"🎯 **To'g'ri Javob:** {current_fc['a']}",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "flash_next")
async def next_flashcard(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(fc_index=data.get("fc_index") + 1)
    await send_flashcard_front(callback, state)

@router.callback_query(F.data.startswith("flash_tts_"))
async def flashcard_tts(callback: CallbackQuery, state: FSMContext):
    """Audio Flashcards (20-funksiya): Savolni ovozli qilib yuborish"""
    data = await state.get_data()
    index = data.get("fc_index")
    current_fc = data.get("flashcards")[index]
    
    # gTTS orqali inglizcha yoki o'zbekcha matnni audio qilish (standart en)
    tts = gTTS(text=current_fc['q'], lang='en')
    file_path = f"tts_{current_fc['id']}.mp3"
    tts.save(file_path)
    
    audio_file = FSInputFile(file_path)
    await callback.message.reply_audio(audio_file, caption="🔊 Savolning ovozli ko'rinishi")
    
    # Vaqtinchalik faylni o'chirish
    if os.path.exists(file_path):
        os.remove(file_path)
  
