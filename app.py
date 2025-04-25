import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"

# Load campus data
with open("campus_data.json", "r") as f:
    data = json.load(f)

# Build prompt payload for Groq AI
def build_prompt(question):
    system_msg = {
        "role": "system",
        "content": (
            "You are a helpful KLNCE Campus Assistant Bot using KLNCE data. "
            "Answer queries about events, schedules, sports, and directions."
        )
    }
    kb = json.dumps({
        k: data[k]
        for k in [
            "events",
            "schedules",
            "directions",
            "sports"
        ]
    })
    return [
        system_msg,
        {"role": "user", "content": f"{question}\nHere is KLNCE data:\n{kb}"}
    ]

# Query the Groq API
def ask_bot(question):
    resp = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": build_prompt(question),
            "temperature": 0.3
        }
    )
    return resp.json()["choices"][0]["message"]["content"]

# Display images based on question/answer content
def show_images(question, answer):
    text = (question + answer).lower()

    def show_list(items, key):
        for item in items:
            if item[key].lower() in text:
                st.image(item["image"], caption=item[key], use_container_width=True)

    show_list(data["events"], "title")

    if "schedule" in text or any(day in text for day in data["schedules"]):
        for day, info in data["schedules"].items():
            if day in text:
                st.image(info["image"], caption=f"Schedule: {day.capitalize()}", use_container_width=True)

    for section in ["directions"]:
        for key, info in data[section].items():
            if key.replace("_", " ") in text:
                st.image(info.get("image"), caption=info.get("info") or key.capitalize(), use_container_width=True)

    for sport, img in data["sports"].items():
        if sport.replace("_", " ") in text:
            st.image(img, caption=sport.replace("_", " ").capitalize(), use_container_width=True)

# Streamlit page setup
st.set_page_config(page_title="KLNCE Campus Assistant", page_icon="🎓", layout="centered")

# --- Stylish Header with Light Colors and Gradient ---
st.markdown("""
    <style>
        .header-container {
            background: linear-gradient(to right, #e0f7fa, #e3f2fd);
            padding: 20px 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            border: 1px solid #cce;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        }
        .header-title {
            font-size: 32px;
            font-weight: bold;
            color: #004d99;
        }
        .header-quote {
            font-size: 16px;
            color: #555;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Header layout
col1, col2 = st.columns([1, 8])
with col1:
    logo_path = "images/logo/klncelogo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=60)
with col2:
    st.markdown("""
        <div class="header-container">
            <div class="header-title">🎓 KLNCE Campus Assistant Bot</div>
            <div class="header-quote">"Empowering Students with Knowledge 💡📚" <br>
            "Explore our campus with a smile 😊🎉"</div>
        </div>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 📘 About")
st.sidebar.write("Your smart assistant for KLN College of Engineering (KLNCE) campus info!")

# --- Stylish Input Area ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #444;'>Ask me anything about KLNCE 🔍:</h4>", unsafe_allow_html=True)

query = st.text_input("")

# --- Bot Response and Image Display ---
if query:
    with st.spinner("🤖 Thinking..."):
        answer = ask_bot(query)

    st.markdown(
        f"<div style='background-color: #f0f4f8; padding: 15px; border-radius: 12px; border: 1px solid #d0dce5;'>"
        f"<strong>🤖 Bot:</strong><br>{answer}</div>",
        unsafe_allow_html=True
    )

    show_images(query, answer)

# --- Footer ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; color: grey;'>"
    "🌐 Powered by Groq AI • Built with ❤️ for KLN College of Engineering"
    "</div>",
    unsafe_allow_html=True
)
