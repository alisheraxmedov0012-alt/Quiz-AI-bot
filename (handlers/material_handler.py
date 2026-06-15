# handlers/material_handler.py ichiga qo'shing:

from parser import parse_manual_keys

@router.callback_query(F.data == "key_manual", StudyPilotStates.choosing_key_method)
async def ask_for_manual_keys(callback: CallbackQuery, state: FSMContext):
    """Manual kalitlarni kiritishni so'rash"""
    await callback.message.edit_text(
        "✍️ Iltimos, test kalitlarini quyidagi formatlardan birida yuboring:\n\n"
        "<code>1-A\n2-B\n3-C</code>\n"
        "yoki\n"
        "<code>1.A, 2.B, 3.C</code>"
    )
    await state.set_state(StudyPilotStates.waiting_for_manual_keys)

@router.message(F.text, StudyPilotStates.waiting_for_manual_keys)
async def process_manual_keys(message: Message, state: FSMContext):
    """Kiritilgan matnli kalitlarni qayta ishlash"""
    raw_keys_text = message.text
    keys_dict = parse_manual_keys(raw_keys_text)
    
    if not keys_dict:
        await message.answer("❌ Kalitlar aniqlanmadi. Iltimos, formatni tekshirib qaytadan yuboring (Masalan: 1-A, 2-B).")
        return

    data = await state.get_data()
    raw_text = data.get("raw_text")
    
    # Birinchi navbatda matndan savollarni regex bilan ajratamiz
    parsed_questions = parse_raw_text_to_questions(raw_text)
    
    if not parsed_questions:
        await message.answer("❌ Afsuski, yuborilgan asosiy matndan test savollari ajratib olinmadi.")
        return
        
    # Ajratilgan savollarga manual kalitlarni biriktirish
    for index, q in enumerate(parsed_questions, start=1):
        if index in keys_dict:
            q['correct'] = keys_dict[index]
            q['confidence'] = 1.0  # Foydalanuvchi o'zi kiritgan bo'lsa, ishonch 100%
            
    await state.update_data(parsed_questions=parsed_questions)
    
    # Bo'limlarga ajratish menyusiga o'tkazish
    total_q = len(parsed_questions)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔢 10 tadan", callback_data="chunk_10")],
        [InlineKeyboardButton(text="🔢 25 tadan", callback_data="chunk_25")],
        [InlineKeyboardButton(text="🌐 Hammasi bitta", callback_data="chunk_all")]
    ])
    
    await message.answer(
        f"✅ {len(keys_dict)} ta javob kaliti savollarga muvaffaqiyatli biriktirildi!\n"
        f"📦 Jami savollar soni: {total_q} ta.\n\n"
        f"Ularni nechtadan bo'limlarga ajratamiz?", 
        reply_markup=keyboard
    )
    await state.set_state(StudyPilotStates.choosing_chunk_size)
  
