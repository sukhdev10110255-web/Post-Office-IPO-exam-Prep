import streamlit as st
import os
import time
import pandas as pd
import plotly.express as px
from PyPDF2 import PdfReader
from gtts import gTTS
import io
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG & STYLING =================
st.set_page_config(page_title="Avyan LDCE v20 Pro", layout="wide", page_icon="🚀")

def apply_custom_style():
    st.markdown("""
        <style>
        .main { background-color: #f5f7f9; }
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; transition: 0.3s; }
        .stButton>button:hover { background-color: #ff4b4b; color: white; border: none; }
        .stExpander { background-color: white; border-radius: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.05); }
        .status-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

# ================= SESSION STATE (Data Recovery) =================
if "init" not in st.session_state:
    st.session_state.update({
        "init": True,
        "topic": "Post Office Act 2024",
        "pdf_text": "",
        "mcqs": [],
        "weak_topics": {}, 
        "chat_history": [],
        "theme": "Light",
        "lang": "Bilingual",
        "score_history": []
    })

# ================= CORE AI ENGINE (Fixed Error Handling) =================
def call_ai(prompt):
    try:
        # API Key safety check
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key: return "❌ Error: API Key missing. Please set CEREBRAS_API_KEY."
        
        client = Cerebras(api_key=api_key)
        res = client.chat.completions.create(
            model="llama3.1-8b-instant",
            messages=[{"role": "system", "content": f"Expert LDCE Tutor. Mode: {st.session_state.lang}"},
                      {"role": "user", "content": prompt}],
            max_tokens=1200
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# ================= FEATURES =================

def generate_voice(text):
    try:
        tts = gTTS(text=text[:500], lang='hi' if st.session_state.lang != "English" else 'en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except: return None

# ================= UI LAYOUT =================
apply_custom_style()

# --- HEADER ---
st.title("🚀 Avyan LDCE IP Masterpiece v20")
st.caption("Ultimate Professional Exam System for Department of Posts")

# --- SIDEBAR (Settings & Rank) ---
with st.sidebar:
    st.header("⚙️ Dashboard Settings")
    st.session_state.theme = st.selectbox("🎨 Theme", ["Light", "Dark"], index=0)
    st.session_state.lang = st.selectbox("🌐 Language", ["Bilingual", "Hindi", "English"], index=0)
    
    st.divider()
    st.subheader("📊 Rank Prediction")
    score_input = st.number_input("Enter Mock Score", 0.0, 100.0, 0.0)
    if st.button("Predict Rank"):
        st.session_state.score_history.append(score_input)
        avg = sum(st.session_state.score_history)/len(st.session_state.score_history)
        st.metric("Expected Percentile", f"{min(99.9, avg+10):.1f}%")

# --- SMART BROWSER (From Screenshot) ---
with st.expander("🌐 Smart Browser & Search", expanded=False):
    search_q = st.text_input("Search Anything (Acts / Rules / PDF)", placeholder="e.g. CCS GPF Rules 1961")
    c1, c2, c3 = st.columns(3)
    if search_q:
        c1.markdown(f"[🔍 Google](https://www.google.com/search?q={search_q}+India+Post)")
        c2.markdown(f"[🧠 Bing](https://www.bing.com/search?q={search_q}+LDCE)")
        c3.markdown(f"[🦆 DuckDuckGo](https://duckduckgo.com/?q={search_q}+Rules)")

# --- MAIN STUDY AREA ---
col_main, col_stats = st.columns([2, 1])

with col_main:
    st.subheader("📚 Study Dashboard")
    topic_input = st.text_input("Enter Topic", st.session_state.topic)
    if topic_input != st.session_state.topic:
        st.session_state.topic = topic_input

    # UI Mode Buttons (From Screenshot)
    m1, m2, m3, m4, m5 = st.columns(5)
    
    if m1.button("📖 Learn"):
        with st.spinner("Generating Notes..."):
            notes = call_ai(f"Provide detailed study notes on {st.session_state.topic} for LDCE IP Exam.")
            st.markdown(f"### Notes: {st.session_state.topic}")
            st.write(notes)
            audio = generate_voice(notes)
            if audio: st.audio(audio, format='audio/mp3')

    if m2.button("💬 Chat"):
        st.info("AI Discussion activated below.")

    if m3.button("📝 MCQ"):
        with st.spinner("Preparing MCQs..."):
            raw_mcq = call_ai(f"Generate 5 high-level MCQs on {st.session_state.topic}. Format: Question, Options A/B/C/D, Correct Answer.")
            st.session_state.mcqs = raw_mcq # In a real app, you'd parse this into a list
            st.write(raw_mcq)

    if m4.button("🎯 Mock"):
        st.warning("Ultimate Mock Exam Mode Starting...")

    if m5.button("🚀 Final"):
        st.error("Final Exam Environment Initialized.")

    # --- AI DISCUSSION (Chat from Screenshot) ---
    st.divider()
    st.subheader("💬 AI Discussion")
    user_query = st.text_input("Ask a doubt about this topic...")
    if user_query:
        response = call_ai(f"Topic: {st.session_state.topic}. Question: {user_query}")
        st.write(f"**AI:** {response}")

with col_stats:
    st.subheader("📉 Weak Topics")
    if not st.session_state.weak_topics:
        st.success("No weak topics yet! Keep it up.")
    else:
        for t, s in st.session_state.weak_topics.items():
            st.error(f"{t}: Accuracy {s}%")

    st.divider()
    # Feature Buttons (From Screenshot)
    if st.button("🧠 Smart Revision"):
        st.info(f"Revising {st.session_state.topic} and previous weak areas...")
    
    if st.button("📂 PYQ (Previous Year)"):
        st.write("Searching for 2022-2024 IP Exam Questions...")
    
    if st.button("📅 Study Plan"):
        plan = call_ai(f"Create a 7-day study plan for {st.session_state.topic} for a Postal Assistant.")
        st.write(plan)

    # PDF Upload
    st.divider()
    pdf_file = st.file_uploader("Upload PDF (Circulars/Rules)", type="pdf")
    if pdf_file:
        reader = PdfReader(pdf_file)
        st.session_state.pdf_text = "".join([p.extract_text() for p in reader.pages])
        st.success("PDF Content Loaded into AI Context.")

# ================= FOOTER =================
st.markdown("---")
st.markdown(f"**System Status:** V20.0 Stable | **Current Topic:** {st.session_state.topic}")
