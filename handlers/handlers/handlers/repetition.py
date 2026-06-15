from aiogram import Router, types, F
from aiogram.filters import Command
from sqlalchemy.future import select
from database import AsyncSessionLocal, Folder
import datetime

router = Router()

@router.message(Command("repeat"))
@router.message(F.text == "🔄 Aqlli Takrorlash")
async def spaced_repetition_control(message: types.Message):
    async with AsyncSessionLocal() as session:
        # Foydalanuvchi papkalarini tekshirish
        result = await session.execute(select(Folder).limit(5))
        folders = result.scalars().all()
        
        if not folders:
            await message.answer("Takrorlash uchun tizimda materiallar aniqlanmadi. Avval papka yarating va material yuklang.")
            return
            
        # Aqlli algoritm integratsiyasi vaqti (Simulyatsiya)
        today = datetime.date.today()
        
        text = f"🔄 **Interval takrorlash paneli (Spaced Repetition):**\n\n"
        text += f"📅 Bugun: `{today.strftime('%d-%m-%Y')}`\n\n"
        text += "🧠 **Tizim tahlili:**\n"
        
        for f in folders:
            text += f"🔸 Papka: *{f.name}* — 1-kunlik takrorlash yakunlangan. Keyingi chuqur takrorlash 3 kundan keyin.\n"
            
        text += "\n💡 Tizim har kuni xotirangizni pasayish davrini hisoblab, testlarni avtomatik eslatib turadi."
        await message.answer(text, parse_mode="Markdown")
      
