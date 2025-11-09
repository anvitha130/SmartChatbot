# main_functions.py

def detect_language(text):
    # Very simple demo logic
    text = text.lower()
    if any(word in text for word in ["hola", "gracias", "adios"]):
        return "es"  # Spanish
    elif any(word in text for word in ["bonjour", "merci", "salut"]):
        return "fr"  # French
    else:
        return "english"


def translate_to_english(text):
    # Pretend translation
    translations = {
        "hola": "Hello",
        "bonjour": "Hello",
        "gracias": "Thank you",
        "merci": "Thank you"
    }
    for word, meaning in translations.items():
        if word in text.lower():
            return meaning
    return text


def get_advice(language):
    if language == "es":
        return "Consejo: sigue aprendiendo cada día."
    elif language == "fr":
        return "Conseil: continuez à apprendre chaque jour."
    else:
        return "Advice: Keep learning every day!"
