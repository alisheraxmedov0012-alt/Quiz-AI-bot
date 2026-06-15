import httpx
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import StudyPilotStates
from config import OPENROUTER_API_KEY

router = Router()

@router.message(F.text.startswith("/ask_teacher"))
async def ai_teacher_explain(message: Message):
    """AI Teacher (22-funksiya): Istalgan mavzuni yoki savolni AI tushuntirib beradi"""
    user_query = message.text.replace("/ask_teacher", "").strip()
    
    if not user_query:
        await message.answer("🤖 Iltimos, so'ramoqchi bo'lgan narsangizni yozing.\nMisol: `/ask_teacher Integral nima?`", parse_mode="Markdown")
        return
        
    await message.answer("🧠 **AI O'qituvchi o'ylamoqda...**")
    
    prompt = f"Sen professional o'qituvchisan. Quyidagi tushunchani talabaga juda sodda, qiziqarli va misollar bilan tushuntirib ber:\n\n{user_query}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "google/gemini-2.5-flash",
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30.0
            )
            res_json = response.json()
            explanation = res_json['choices'][0]['message']['content']
            await message.answer(f"👨‍🏫 **AI O'qituvchi javobi:**\n\n{explanation}")
        except Exception as e:
            await message.answer("❌ AI bilan ulanishda xatolik yuz berdi.")
          
