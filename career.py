import streamlit as st
import numpy as np
from PIL import Image
import easyocr
from gtts import gTTS
import google.generativeai as genai
import speech_recognition as sr
from langdetect import detect
import sqlite3
import datetime


# ======================================================
# 🔑 Configure Gemini API
# ======================================================
genai.configure(api_key="AIzaSyBJXfFW1zd6V3IRzF_yYGUx1CIX0XWistI")
MODEL_NAME = "gemini-2.5-flash" # ✅ Fixed

# ======================================================
# 🧠 Initialize OCR
# ======================================================
reader = easyocr.Reader(['en'], gpu=False)

# ======================================================
# 🎙 Voice-to-Text
# ======================================================
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 Listening... please speak clearly.")
        audio = r.listen(source, phrase_time_limit=5)
        try:
            text = r.recognize_google(audio)
            st.success(f"🗣 You said: {text}")
            return text
        except Exception:
            st.warning("❗ Sorry, could not understand. Please try again.")
            return ""

# ======================================================
# 🔊 Text-to-Speech
# ======================================================
def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3")
    except Exception as e:
        st.error(f"TTS Error: {e}")

# ======================================================
# 🌐 Language Detection
# ======================================================
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

# ======================================================
# 🌍 Translate to English
# ======================================================
def translate_to_english(text, detected_lang):
    if detected_lang != "en":
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            prompt = f"Translate this text to English:\n{text}"
            result = model.generate_content(prompt)
            return result.text.strip()
        except Exception as e:
            st.error(f"Translation failed: {e}")
            return text
    return text

# ======================================================
# 💬 AI Career Advice
# ======================================================
def get_ai_response(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        result = model.generate_content(prompt)
        return result.text.strip()
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return None

# ======================================================
# 🎨 Streamlit Setup
# ======================================================
st.set_page_config(page_title="AI Career Counselor", layout="centered")

st.markdown("""
<h1 style='text-align:center; color:white;'>🎓 AI Career Counselor & Resume Advisor</h1>
<p style='text-align:center;'>Ask me anything about your career, in any language 🌍</p>
<hr style='border:1px solid white;' />
<style>
    .stApp {
        background: linear-gradient(to right, #8e2de2, #ff6a88);
        font-family: 'Segoe UI', sans-serif;
        color: white;
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        background-color: #4b0055;
        color: white;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #4b0055 !important;
        color: white !important;
    }
    .stButton>button {
        background-color: #ffdd57;
        color: black;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# ======================================================
# 🧭 Sidebar & Inputs
# ======================================================
mode = st.sidebar.radio("Choose Input Mode", ["Text", "Image", "Voice"])

lang_map = {
    "en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French",
    "de": "German", "ta": "Tamil", "te": "Telugu", "ml": "Malayalam"
}

selected_lang = st.selectbox("🌐 Output Language", list(lang_map.values()), index=0)
output_language_code = list(lang_map.keys())[list(lang_map.values()).index(selected_lang)]

final_input = ""

if mode == "Text":
    final_input = st.text_input("💬 Type your career question:")
elif mode == "Image":
    file = st.file_uploader("🖼 Upload an image", type=["png", "jpg", "jpeg"])
    if file:
        img = Image.open(file)
        st.image(img, caption="Uploaded Image", use_column_width=True)
        with st.spinner("📖 Extracting text..."):
            text = reader.readtext(np.array(img), detail=0)
            final_input = " ".join(text)
            st.success("✅ Text extracted from image.")
elif mode == "Voice":
    st.markdown("🎙️ **Voice Input**")

    if "voice_input" not in st.session_state:
        st.session_state.voice_input = ""

    if st.button("🎤 Speak Now"):
        st.session_state.voice_input = listen()

    final_input = st.session_state.voice_input
# ======================================================
# 🚀 Generate Output
# ======================================================
submit = st.button("🎯 Get Career Advice")
voice_enabled = st.checkbox("🔈 Speak the Response")

if submit:
    if not final_input.strip():
        st.warning("⚠️ Please provide your input first.")
    else:
        with st.spinner("🧠 Thinking..."):
            detected_lang = detect_language(final_input)
            english_input = translate_to_english(final_input, detected_lang)
            prompt = f"""
You are a helpful AI Career Counselor.
Respond in language code '{output_language_code}'.
User's question: "{english_input}"

Include:
1. Friendly and clear advice.
2. 2–3 actionable next steps.
3. Optionally, suggest online resources.
"""
            response = get_ai_response(prompt)
            if response:
                st.success("✅ Here's your career advice:")
                st.text_area("📄 Advice", value=response, height=300)
                st.download_button("📥 Download Advice", data=response, file_name="career_advice.txt")
                if voice_enabled:
                    speak_text(response, output_language_code)
            else:
                st.error("⚠️ No valid response from Gemini. Check logs.")

# ======================================================
# ⚙️ Footer
# ======================================================
st.markdown("---")
st.markdown("<p style='text-align:center;'>🔧 Built with ❤ using Streamlit, Gemini, gTTS, EasyOCR & Speech Recognition</p>", unsafe_allow_html=True)
