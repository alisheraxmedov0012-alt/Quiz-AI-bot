from aiogram import BaseMiddleware
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

REQUIRED_CHANNELS = ["-100123456789", "-100987654321"] # Kanallar ID ro'yxati

class SubCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id
        bot = data['bot']
        
        # Bu yerda har safar bazaga urmaslik uchun cache ishlatsa bo'ladi
        for channel in REQUIRED_CHANNELS:
            try:
                member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
                if member.status in ["left", "kicked"]:
                    raise Exception()
            except Exception:
                # Agar bittasidan ham o'tmagan bo'lsa, to'xtatish
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="1-Kanal", url="https://t.me/Samarqandkvartiralarelonlari")],
                    [InlineKeyboardButton(text="2-Kanal", url="https://t.me/Toshkent_kvartira_ijara_elonlari")],
                    [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub_again")]
                ])
                return await event.answer("⚠️ **Botdan foydalanish uchun homiy kanallarga obuna bo'lishingiz shart!**", reply_markup=keyboard)
                
        return await handler(event, data)

