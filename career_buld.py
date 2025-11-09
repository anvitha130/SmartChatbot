import streamlit as st
import numpy as np
from PIL import Image
import easyocr
from gtts import gTTS
import os
import google.generativeai as genai
import speech_recognition as sr
from langdetect import detect

# =========================
# 🔑 Configure Gemini API
# =========================
genai.configure(api_key="AIzaSyBJXfFW1zd6V3IRzF_yYGUx1CIX0XWistI")  # Replace with your actual API key

# Use latest valid Gemini model
GEMINI_MODEL = "models/gemini-1.5-pro"


# =========================
# 🧠 Initialize OCR
# =========================
reader = easyocr.Reader(['en'], gpu=False)

# =========================
# 🎙 Voice-to-Text
# =========================
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 Listening... Please speak clearly.")
        audio = r.listen(source, phrase_time_limit=6)
        try:
            text = r.recognize_google(audio)
            st.success(f"🗣 You said: {text}")
            return text
        except Exception:
            st.warning("❗ Could not understand your speech. Please try again.")
            return ""

# =========================
# 🔊 Text-to-Speech
# =========================
def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3")
    except Exception as e:
        st.error("TTS Error")
        st.text(str(e))

# =========================
# 🌐 Detect Language
# =========================
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

# =========================
# 🌍 Translate Non-English → English
# =========================
def translate_to_english(text, detected_lang):
    if detected_lang != "en":
        prompt = f"Translate this to English:\n{text}"
        model = genai.GenerativeModel(GEMINI_MODEL)
        result = model.generate_content(prompt)
        return result.text.strip()
    return text

# =========================
# 💬 Get AI Career Advice
# =========================
def get_ai_response(prompt):
    model = genai.GenerativeModel(GEMINI_MODEL)
    result = model.generate_content(prompt)
    return result.text.strip()

# =========================
# 🎨 Streamlit UI
# =========================
st.set_page_config(page_title="AI Career Counselor", layout="centered")
st.markdown("""
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

# =========================
# 🧭 Header
# =========================
st.markdown("""
<h1 style='text-align:center; color:white;'>🎓 AI Career Counselor & Resume Advisor</h1>
<p style='text-align:center;'>Smart, multilingual guidance for your career journey 🌍</p>
<hr style='border:1px solid white;' />
""", unsafe_allow_html=True)

# =========================
# 🧩 Sidebar
# =========================
mode = st.sidebar.radio("Choose Input Mode", ["Text", "Image", "Voice"])

# Language Options
lang_map = {
    "en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French",
    "de": "German", "ta": "Tamil", "te": "Telugu", "ml": "Malayalam"
}
selected_lang = st.selectbox("🌐 Output Language", list(lang_map.values()), index=0)
output_language_code = list(lang_map.keys())[list(lang_map.values()).index(selected_lang)]

final_input = ""

# =========================
# 🧾 Handle Input Modes
# =========================
if mode == "Text":
    st.markdown("💬 **Text Input**")
    final_input = st.text_input("Type your career question:")

elif mode == "Image":
    st.markdown("🖼 **Image Upload**")
    image_file = st.file_uploader("Upload a resume or job description image", type=["png", "jpg", "jpeg"])
    if image_file:
        img = Image.open(image_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)
        with st.spinner("📖 Extracting text..."):
            result = reader.readtext(np.array(img), detail=0)
            final_input = " ".join(result)
            st.success("✅ Text extracted from image.")

elif mode == "Voice":
    st.markdown("🎙️ **Voice Input**")
    if st.button("🎤 Speak Now"):
        final_input = listen()

# =========================
# 🚀 Generate Response
# =========================
submit = st.button("🎯 Get Career Advice")
voice_enabled = st.checkbox("🔈 Speak the Response")

if submit:
    if not final_input.strip():
        st.warning("⚠️ Please provide input through your selected mode.")
    else:
        with st.spinner("🧠 Thinking..."):
            try:
                detected_lang = detect_language(final_input)
                english_input = translate_to_english(final_input, detected_lang)

                prompt = f"""
                You are a multilingual AI Career Counselor. Provide your response in the language code '{output_language_code}'.
                User's question: "{english_input}"

                Include:
                1. Clear, friendly career advice.
                2. Suggested next steps or actionable recommendations.
                3. (Optional) 2–3 helpful online resources.
                """

                response = get_ai_response(prompt)
                st.success("✅ Here's your AI Career Advice:")
                st.text_area("📄 Advice", value=response, height=300)

                st.download_button("📥 Download Advice", data=response, file_name="career_advice.txt")

                if voice_enabled:
                    speak_text(response, output_language_code)

            except Exception as e:
                raise RuntimeError("Translation failed: " + str(e)) 


# =========================
# ⚙️ Footer
# =========================
st.markdown("---")
st.markdown(
    "<p style='text-align:center;'>🔧 Built with ❤ using Streamlit, Gemini, gTTS, EasyOCR & Speech Recognition</p>",
    unsafe_allow_html=True
)
