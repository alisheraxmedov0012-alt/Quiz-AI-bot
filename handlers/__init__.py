from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from sqlalchemy.future import select
from sqlalchemy.sql import func
import datetime

# Shuningdek, loyihaning eski bor fayllaridan routerlarni import qilamiz
from .material_handler import router as material_handler_router
from .study_mode import router as study_mode_router
from .flashcards import router as flashcards_router
from .ai_features import router as ai_features_router
from .exam_mode import router as exam_mode_router
from .gamification import router as gamification_router

# database ulanishi (agar loyihangizda mavjud bo'lsa, xato bermasligi uchun try-except ichida)
try:
    from database import AsyncSessionLocal, User, TestBank, Question, Folder
except ImportError:
    AsyncSessionLocal = None

# --- YANGI KUCHLI ROUTERLARNI SHU YERNING O'ZIDA REZERV QILAMIZ ---
start_router = Router()
editor_handler_router = Router()
error_bank_router = Router()
repetition_router = Router()
bookmarks_router = Router()
search_router = Router()
battle_node_router = Router()
daily_challenge_router = Router()
referral_router = Router()
admin_panel_router = Router()

# ==========================================
# 1. START LOGIKASI
# ==========================================
def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📁 Mening Papkalarim")
    builder.button(text="📝 Kunlik Vazifa")
    builder.button(text="🔄 Aqlli Takrorlash")
    builder.button(text="⚔️ Quiz Battle")
    builder.button(text="📊 Xatolar Banki")
    builder.button(text="🔍 Qidiruv")
    builder.button(text="🔗 Do'stlarni taklif qilish")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

@start_router.message(CommandStart())
async def cmd_start(message: types.Message):
    username = message.from_user.username or "Foydalanuvchi"
    text = f"🚀 **Quiz AI** platformasiga xush kelibsiz, {username}!\n\nBu yerda siz o'quv materiallari, PDF va matnlarni yuklab, ulardan AI yordamida testlar yaratishingiz mumkin."
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

# ==========================================
# 2. EDITOR LOGIKASI
# ==========================================
@editor_handler_router.message(Command("edit_test"))
@editor_handler_router.message(F.text == "📝 Test Tahrirlash")
async def list_tests_for_edit(message: types.Message):
    await message.answer("📝 **Test tahrirlash paneli:**\n\nTizimda tahrirlash uchun hozircha testlar topilmadi.")

# ==========================================
# 3. ERROR BANK LOGIKASI
# ==========================================
@error_bank_router.message(Command("errors"))
@error_bank_router.message(F.text == "📊 Xatolar Banki")
async def show_error_bank(message: types.Message):
    await message.answer("🌟 **Ajoyib!** Xatolar bankingiz bo'sh. Siz barcha testlarni yuqori natija bilan yechgansiz!", parse_mode="Markdown")

# ==========================================
# 4. REPETITION LOGIKASI
# ==========================================
@repetition_router.message(Command("repeat"))
@repetition_router.message(F.text == "🔄 Aqlli Takrorlash")
async def spaced_repetition_control(message: types.Message):
    today = datetime.date.today().strftime('%d-%m-%Y')
    text = f"🔄 **Interval takrorlash paneli (Spaced Repetition):**\n\n📅 Bugun: `{today}`\n\n🧠 Bugun takrorlash uchun materiallar mavjud emas. Miya dam olmoqda!"
    await message.answer(text, parse_mode="Markdown")

# ==========================================
# 5. BOOKMARKS LOGIKASI
# ==========================================
@bookmarks_router.message(Command("bookmarks"))
async def view_bookmarks(message: types.Message):
    await message.answer("🔖 **Saqlangan xatcho'plar bo'limi**\n\nBu yerda siz belgilab qo'ygan murakkab formulalar va savollar saqlanadi.")

# ==========================================
# 6. SEARCH LOGIKASI
# ==========================================
@search_router.message(Command("search"))
@search_router.message(F.text == "🔍 Qidiruv")
async def start_search(message: types.Message):
    await message.answer("🔍 Qidirmoqchi bo'lgan faningiz, kalit so'zingiz yoki test sarlavhasini kiriting:")

# ==========================================
# 7. BATTLE NODE LOGIKASI
# ==========================================
@battle_node_router.message(Command("battle"))
@battle_node_router.message(F.text == "⚔️ Quiz Battle")
async def start_quiz_battle(message: types.Message):
    text = "⚔️ **Quiz AI — Jonli Bellashuv Arenasi (1v1)**\n\nTasodifiy raqib bilan test yechish tezligi bo'yicha bellashing!"
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Raqib qidirish", callback_data="battle_matchmaking")
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# ==========================================
# 8. DAILY CHALLENGE LOGIKASI
# ==========================================
@daily_challenge_router.message(Command("daily"))
@daily_challenge_router.message(F.text == "📝 Kunlik Vazifa")
async def show_daily_challenge(message: types.Message):
    text = "📅 **Bugungi Kunlik Vazifangiz:**\n\n1. AI yordamida yangi 1 ta PDF faylni tahlil qiling.\n\n🎁 Mukofot: `+150 XP`"
    await message.answer(text, parse_mode="Markdown")

# ==========================================
# 9. REFERRAL LOGIKASI
# ==========================================
@referral_router.message(Command("invite"))
@referral_router.message(F.text == "🔗 Do'stlarni taklif qilish")
async def generate_referral_link(message: types.Message):
    bot_info = await message.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=ref_{message.from_user.id}"
    text = f"👥 **Do'stlarni taklif qilish tizimi**\n\n🔗 Sizning shaxsiy taklif havolangiz:\n`{referral_link}`"
    await message.answer(text, parse_mode="Markdown")

# ==========================================
# 10. ADMIN PANEL LOGIKASI
# ==========================================
ADMIN_ID = 8344095954  # O'zingizning Telegram ID'ingiz

@admin_panel_router.message(Command("admin"))
async def open_admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⚠️ Kechirasiz, ushbu buyruq faqat loyiha administratori uchun ochiq!")
        return
    await message.answer("👑 **Quiz AI — Administrator Boshqaruv Paneli**\n\n/broadcast — Xabar yuborish")
    
# ==========================================
# OBUNANI QAYTA TEKSHIRISH TUGMASI LOGIKASI
# ==========================================
# F.data o'rniga xavfsiz lambda funksiyasidan foydalanamiz, shunda import shart bo'lmaydi:
@start_router.callback_query(lambda call: call.data == "check_sub_again")
async def check_subscription_callback(call): # types. olib tashlandi
    user_id = call.from_user.id
    bot = call.message.bot
    channels = ["-1003372913142", "-1003877501774"]
    
    all_subscribed = True
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                all_subscribed = False
                break
        except Exception:
            all_subscribed = False
            break

    if all_subscribed:
        await call.answer("🎉 Tabriklaymiz, barcha kanallarga a'zo bo'ldingiz!", show_alert=True)
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer("🚀 Obuna tasdiqlandi! Botni qayta ishga tushirish uchun /start buyrug'ini bosing.")
    else:
        await call.answer("❌ Siz hali barcha kanallarga obuna bo'lmagansiz!", show_alert=True)
        
# --- GLOBAL ROUTERLAR RO'YXATI (main.py ko'radigan qism) ---
all_routers = [
    material_handler_router,
    study_mode_router,
    flashcards_router,
    ai_features_router,
    exam_mode_router,
    gamification_router,
    start_router,
    editor_handler_router,
    error_bank_router,
    repetition_router,
    bookmarks_router,
    search_router,
    battle_node_router,
    daily_challenge_router,
    referral_router,
    admin_panel_router
]
