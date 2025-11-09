import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from database import create_table, insert_query, get_queries

# Load environment variables (API key)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize DB
create_table()

# Streamlit UI
st.set_page_config(page_title="Smart Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Smart Data Chatbot")

# User input fields
username = st.text_input("Enter your name:")
mode = st.selectbox("Choose mode:", ["Chat", "Analysis", "Explain"])
question = st.text_area("Ask your question here:")

if st.button("Get Answer"):
    if not username or not question:
        st.warning("Please enter both your name and question.")
    else:
        try:
            # ✅ Use the latest supported Gemini model
            model = genai.GenerativeModel("gemini-2.0-flash")

            # ✅ Generate AI response
            response = model.generate_content(question)
            simulated_response = response.text

            # ✅ Display response
            st.success("**AI Response:**")
            st.write(simulated_response)

            # ✅ Save to database
            insert_query(username, question, simulated_response, mode)
            st.info("Your query has been saved successfully!")

        except Exception as e:
            st.error(f"Error: {e}")

# Optional section to view past questions
if st.checkbox("Show my past queries"):
    if username:
        history = get_queries(username)
        if history:
            for q, r, m, t in history:
                st.markdown(f"**[{t}] ({m})** ❓ {q}")
                st.markdown(f"🧠 *{r}*")
                st.divider()
        else:
            st.write("No previous queries found.")
    else:
        st.warning("Enter your name to see your past queries.")
        # --- LOGIN SYSTEM (Simple Streamlit Session) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    username_input = st.text_input("Enter your username:")
    password_input = st.text_input("Enter your password:", type="password")
    if st.button("Login"):
        # Simple static login (you can connect to DB later)
        if username_input == "admin" and password_input == "1234":
            st.session_state.logged_in = True
            st.session_state.username = username_input
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()
else:
    st.sidebar.write(f"👋 Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

