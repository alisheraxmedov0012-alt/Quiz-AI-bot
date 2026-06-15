import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/studypilot")

# AI bilan ishlash uchun (masalan OpenRouter orqali)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

