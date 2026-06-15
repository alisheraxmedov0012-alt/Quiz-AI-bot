from aiogram import Router, types, F
from aiogram.filters import Command
from sqlalchemy.future import select
from database import AsyncSessionLocal, Question

router = Router()

@router.message(Command("bookmarks"))
async def view_bookmarks(message: types.Message):
    await message.answer("🔖 **Saqlangan xatcho'plar bo'limi**\n\nBu yerda siz belgilab qo'ygan murakkab formulalar va savollar saqlanadi. Hozircha xatcho'plar bo'sh.")

# Xatcho'pga qo'shish callback funksiyasi
@router.callback_query(F.data.startswith("bookmark_q_"))
async def add_to_bookmark(callback: types.CallbackQuery):
    q_id = int(callback.data.split("_")[2])
    # Kelajakda Bookmarks jadvaliga yoziladi
    await callback.answer("⭐ Savol xatcho'plarga muvaffaqiyatli qo'shildi!", show_alert=True)
  
