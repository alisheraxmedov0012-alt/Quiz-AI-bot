import re
import json
import httpx
from config import OPENROUTER_API_KEY

def parse_raw_text_to_questions(text: str) -> list:
    """
    Standart formatdagi testlarni tezkor regex bilan ajratish.
    Har xil satrdagi savollar va variant ichidagi nuqtalarni ham to'g'ri ajratadi.
    """
    # Savollarni raqamlar bo'yicha bo'lish (1., 2-, 3) variantlari uchun)
    question_blocks = re.split(r'\n(?=\d+[\.\-\)])', text.strip())
    parsed_questions = []

    for block in question_blocks:
        if not block.strip():
            continue

        # Savol matni va variantlar qismini ajratish
        # Variantlar boshlanish joyini qidiramiz (A) yoki A. yoki A-)
        match_options_start = re.search(r'(^|\s)([A-E][\)\.\-])\s', block)
        
        if match_options_start:
            start_idx = match_options_start.start()
            q_text = block[:start_idx].strip()
            options_text = block[start_idx:].strip()
        else:
            # Agar variantlar topilmasa, butun blokni savol deb olamiz
            q_text = block.strip()
            options_text = ""

        # Variantlarni harflar bo'yicha to'g'ri kesib olish (Lookahead yordamida)
        # Bu regex variant ichidagi nuqtalarga chalinmaydi
        options = re.findall(r'([A-E])[\)\.\-]\s*(.*?)(?=\s*[A-E][\)\.\-]\s*|$)', options_text, re.DOTALL)
        
        options_dict = {}
        for opt_letter, opt_val in options:
            options_dict[opt_letter.upper()] = opt_val.strip()
            
        if q_text:
            # Savol boshidagi raqamni tozalash (Masalan: "1. Tizim..." -> "Tizim...")
            clean_q_text = re.sub(r'^\d+[\.\-\)]\s*', '', q_text).strip()
            
            parsed_questions.append({
                "question": clean_q_text,
                "options": options_dict,
                "correct": None  # Kalit keyinroq aniqlanadi
            })
            
    return parsed_questions


async def ask_ai_to_parse_and_solve(text: str) -> list:
    """Regex o'ta olmagan murakkab matnlarni parse qilish va to'g'ri javoblarni AI orqali topish"""
    if not OPENROUTER_API_KEY:
        return []

    prompt = f"""
    Quyidagi matn ichidan test savollari, variantlari va to'g'ri javoblarini aniqlab, ularni FAQAT va FAQAT JSON formatida qaytar.
    Hech qanday qo'shmcha tushuntirish yoki markdown formatsiz javob ber.
    
    Format namunasi:
    [
      {{"question": "Python nima?", "options": {{"A": "Dasturlash tili", "B": "Ilon turi"}}, "correct": "A", "confidence": 0.95}}
    ]
    
    Matn:
    {text}
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "google/gemini-2.5-flash",
        "messages": [{"role": "user", "content": prompt}]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30.0)
            res_json = response.json()
            content = res_json['choices'][0]['message']['content']
            
            # Markdown belgilari bo'lsa tozalash
            clean_content = re.sub(r'```json|```', '', content).strip()
            return json.loads(clean_content)
        except Exception as e:
            print(f"AI Parser xatoligi: {e}")
            return []


def parse_manual_keys(text: str) -> dict:
    """
    Foydalanuvchi yuborgan plain text kalitlarni dict formatiga o'tkazadi.
    Namuna: "1-A\\n2-C" -> {{1: "A", 2: "C"}}
    """
    matches = re.findall(r'(\d+)\s*[\.\-\)\s]*\s*([A-E])', text, re.IGNORECASE)
    
    keys_dict = {}
    for num, letter in matches:
        keys_dict[int(num)] = letter.upper().strip()
        
    return keys_dict
    
