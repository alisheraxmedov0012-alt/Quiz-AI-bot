import re

def parse_raw_text_to_questions(text: str) -> list:
    """
    Oddiy matndan savollar, variantlar qismini regex orqali ajratadi.
    Pattern: 1. Savol... A) ... B) ... formatidagi standart testlar uchun.
    """
    # Savollarni raqamlar bo'yicha bo'lish (1., 2. yoki 1-)
    question_blocks = re.split(r'\n(?=\d+[\.\-\)])', text)
    parsed_questions = []

    for block in question_blocks:
        if not block.strip():
            continue
            
        # Savol matnini topish
        lines = block.strip().split('\n')
        q_text = lines[0]
        
        # Variantlarni bitta satrga yig'ish (agar ular har xil qatorda bo'lsa)
        options_text = " ".join(lines[1:])
        
        # Variantlarni ajratish (A), B), C), D) yoki A., B., C.)
        options = re.findall(r'([A-D][\)\.])\s*([^A-D\)\.]+)', options_text)
        
        options_dict = {}
        for opt_letter, opt_val in options:
            clean_letter = opt_letter.replace(')', '').replace('.', '').strip()
            options_dict[clean_letter] = opt_val.strip()
            
        if q_text and options_dict:
            parsed_questions.append({
                "question": q_text,
                "options": options_dict
            })
            
    return parsed_questions
import re
import json
import httpx
from config import OPENROUTER_API_KEY

def parse_raw_text_to_questions(text: str) -> list:
    """Standart formatdagi testlarni tezkor regex bilan ajratish (Tezlik uchun cache vazifasini o'taydi)"""
    question_blocks = re.split(r'\n(?=\d+[\.\-\)])', text)
    parsed_questions = []

    for block in question_blocks:
        if not block.strip():
            continue
        lines = block.strip().split('\n')
        q_text = lines[0]
        options_text = " ".join(lines[1:])
        options = re.findall(r'([A-D][\)\.])\s*([^A-D\)\.]+)', options_text)
        
        options_dict = {}
        for opt_letter, opt_val in options:
            clean_letter = opt_letter.replace(')', '').replace('.', '').strip()
            options_dict[clean_letter] = opt_val.strip()
            
        if q_text and options_dict:
            parsed_questions.append({
                "question": q_text,
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
    Hech qanday qo'shimcha matn yozma.
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
        "model": "google/gemini-2.5-flash", # Tezkor va arzon model
        "messages": [{"role": "user", "content": prompt}]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30.0)
            res_json = response.json()
            content = res_json['choices'][0]['message']['content']
            # Ba'zan modellar markdown ```json ``` ichida qaytaradi, uni tozalaymiz
            clean_content = re.sub(r'```json|```', '', content).strip()
            return json.loads(clean_content)
        except Exception as e:
            print(f"AI Parser xatoligi: {e}")
            return []
# parser.py faylining oxiriga qo'shing:

def parse_manual_keys(text: str) -> dict:
    """
    Foydalanuvchi yuborgan plain text kalitlarni dict formatiga o'tkazadi.
    Namuna: "1-A\n2-C\n3-D" yoki "1.B 2.A" -> {1: "A", 2: "C", 3: "D"}
    """
    # Raqam va harf juftliklarini topish (Masalan: 1-A, 2.B, 3 C, 4) D)
    matches = re.findall(r'(\d+)\s*[\.\-\)\s]*\s*([A-E])', text, re.IGNORECASE)
    
    keys_dict = {}
    for num, letter in matches:
        keys_dict[int(num)] = letter.upper().strip()
        
    return keys_dict
  
