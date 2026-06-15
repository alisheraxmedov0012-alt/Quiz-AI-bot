from aiogram.fsm.state import State, StatesGroup

class StudyPilotStates(StatesGroup):
    waiting_for_material = State()       # Fayl yoki matn kutish holati
    choosing_folder = State()            # Papka tanlash yoki yangisini ochish
    choosing_key_method = State()        # Kalitni aniqlash usuli (AI yoki Manual)
    waiting_for_manual_keys = State()    # Manual kalit matnini kutish (masalan: 1-A, 2-C)
    choosing_chunk_size = State()        # Bo'limlarga bo'lish sonini tanlash
    main_menu = State()                  # Asosiy menyu holati

