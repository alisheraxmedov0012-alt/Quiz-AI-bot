from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select
from sqlalchemy.sql import func
from database import AsyncSessionLocal, User

router = Router()

ADMIN_ID = 8344095954  # 👈 BU YERGA O'ZINGIZNING HAQIQIY TELEGRAM ID-RAQAMINGIZNI YOZING

class AdminBroadcast(StatesGroup):
    waiting_message = State()

@router.message(Command("admin"))
async def open_admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⚠️ Kechirasiz, ushbu buyruq faqat loyiha administratori uchun ochiq!")
        return
        
    async with AsyncSessionLocal() as session:
        # Umumiy foydalanuvchilar sonini hisoblash
        result = await session.execute(select(func.count(User.id)))
        total_users = result.scalar()
        
    text = (
        "👑 **Quiz AI — Administrator Boshqaruv Paneli**\n\n"
        f"📊 Bot a'zolari jami: `{total_users}` nafar\n\n"
        "**Buyruqlar:**\n"
        "/broadcast — Barcha foydalanuvchilarga reklama/xabar yuborish\n"
        "/stats — Kengaytirilgan SQL statistika"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("📝 Barcha foydalanuvchilarga yuboriladigan xabar matnini (yoki rasmini) kiriting:")
    await state.set_state(AdminBroadcast.waiting_message)

@router.message(AdminBroadcast.waiting_message)
async def perform_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.telegram_id))
        user_ids = result.scalars().all()
        
    success_count = 0
    await message.answer(f"📢 Rassilka boshlandi. Jami manzil: {len(user_ids)} ta...")
    
    for u_id in user_ids:
        try:
            await message.copy_to(chat_id=u_id)
            success_count += 1
        except Exception:
            pass  # Botni blocklagan bo'lsa o'tib ketadi
            
    await message.answer(f"✅ Rassilka yakunlandi! Xabar {success_count} ta foydalanuvchiga muvaffaqiyatli yetib bordi.")
    await state.clear()
  
