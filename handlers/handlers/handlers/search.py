from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select
from database import AsyncSessionLocal, TestBank

router = Router()

class SearchState(StatesGroup):
    waiting_query = State()

@router.message(Command("search"))
@router.message(F.text == "🔍 Qidiruv")
async def start_search(message: types.Message, state: FSMContext):
    await message.answer("🔍 Qidirmoqchi bo'lgan faningiz, kalit so'zingiz yoki test sarlavhasini kiriting:")
    await state.set_state(SearchState.waiting_query)

@router.message(SearchState.waiting_query)
async def process_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    
    async with AsyncSessionLocal() as session:
        # SQL `LIKE` operatori yordamida qidiruv berish
        result = await session.execute(select(TestBank).filter(TestBank.title.ilike(f"%{query}%")).limit(5))
        found_tests = result.scalars().all()
        
        if not found_tests:
            await message.answer(f"❌ '{query}' bo'yicha hech qanday test materiallari topilmadi. Qayta urinib ko'ring.")
            await state.clear()
            return
            
        response = f"🔍 **Qidiruv natijalari ('{query}'):**\n\n"
        for idx, test in enumerate(found_tests, 1):
            response += f"{idx}. 📋 **{test.title}** (Versiya: {test.version})\n"
            
        await message.answer(response, parse_mode="Markdown")
    await state.clear()
  
