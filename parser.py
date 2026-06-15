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
  
