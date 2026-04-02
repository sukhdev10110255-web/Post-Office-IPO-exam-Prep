import streamlit as st
import os
import time
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v25.2", layout="wide", initial_sidebar_state="collapsed")

def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-size: 32px; color: #ff4b4b; padding: 10px; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; border: 1px solid #ccc; }}
        .status-tag {{ font-size: 12px; color: #4caf50; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

# ================= STATE MANAGEMENT =================
if "page" not in st.session_state:
    st.session_state.update({
        "page": "Home",
        "theme": "Light",
        "lang": "Bilingual",
        "selected_paper": None,
        "selected_topic": None,
        "active_model": "Checking...",
        "exam_history": [],
        "weak_topics": set()
    })

# ================= SYLLABUS (Aug 2025 Updates) =================
SYLLABUS_2025 = {
    "Paper 1": ["Post Office Act 2023", "Post Office Rules 2024", "PO Guide Part I & II", "POSB Manual", "IT Modernization 2.0", "DIGIPIN", "PMLA Act 2002"],
    "Paper 2": ["Noting (15 Marks)", "Drafting (15 Marks)", "Major Penalty Charge Sheet (Rule 14)"],
    "Paper 3": ["Constitution of India", "BNSS 2023", "CAT Act 1985", "RTI Act 2005", "CCS Pension Rules 2021", "GFR 2017", "English & Reasoning"]
}

# ================= AUTO-FAILOVER AI ENGINE =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key: return "❌ CEREBRAS_API_KEY missing in Render Settings."
    
    client = Cerebras(api_key=api_key)
    
    # Priority list for Auto-Failover
    models_to_try = [
        "llama-3.3-70b-versatile", # Best Performance
        "llama-3.1-70b-versatile", # Backup 1
        "llama-3.1-8b-instant",    # Backup 2 (Fastest)
        "llama3.1-70b",            # Legacy Name 1
        "llama3.1-8b"              # Legacy Name 2
    ]
    
    for model_name in models_to_try:
        try:
            res = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": "You are an expert Inspector Posts (IP) LDCE Tutor. Provide answers in Hindi and English."},
                          {"role": "user", "content": f"Language: {st.session_state.lang}. Prompt: {prompt}"}],
                max_tokens=2000
            )
            st.session_state.active_model = model_name
            return res.choices[0].message.content
        except Exception:
            # If current model fails, it automatically moves to the next one in list
            continue
            
    return "⚠️ Critical AI Fail: All available models (Failover exhausted). Check API Quota."

# ================= PAGES =================

def show_home():
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Paper 1 (250m)"): navigate_to("Paper", "Paper 1")
    if c2.button("Paper 2 (50m)"): navigate_to("Paper", "Paper 2")
    if c3.button("Paper 3 (300m)"): navigate_to("Paper", "Paper 3")
    
    st.divider()
    st.subheader("📊 Exam Progress")
    if st.session_state.exam_history:
        st.line_chart(st.session_state.exam_history)
    else:
        st.info("Performance data will appear here after your first test.")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Prepare {paper}</h1>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.write("### 📘 Syllabus Topics (Clickable)")
        for topic in SYLLABUS_2025.get(paper, []):
            if st.button(f"📌 {topic}", key=f"p_{topic}"):
                navigate_to("Study", topic)

    with col_b:
        st.write("### 🧠 Smart Revision")
        if st.session_state.weak_topics:
            st.error("Focus Areas:")
            for wt in st.session_state.weak_topics:
                if st.button(f"🔄 Revise {wt}", key=f"r_{wt}"):
                    navigate_to("Study", wt)
        else:
            st.success("No weak topics! Keep studying.")

    st.divider()
    c_back, c_exam = st.columns(2)
    if c_back.button("⬅️ Back Home"): navigate_to("Home")
    if c_exam.button("📝 Take Live Exam"): st.toast("Exam Mode Loading...")

def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["📖 Study Notes", "💬 Chat Doubt"])
    with t1:
        if st.button("✨ Generate AI Notes"):
            with st.spinner(f"Trying Auto-Failover Models..."):
                st.markdown(call_ai(f"Detailed study notes on {topic} for IP Exam."))
    with t2:
        q = st.chat_input("Ask anything...")
        if q: st.write(call_ai(f"Doubt about {topic}: {q}"))

    if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def navigate_to(page, data=None):
    st.session_state.page = page
    if page == "Paper": st.session_state.selected_paper = data
    if page == "Study": st.session_state.selected_topic = data
    st.rerun()

# ================= ROUTER =================
apply_android_style()
st.sidebar.markdown(f"**System Status:** Online")
st.sidebar.markdown(f"**Active AI:** `{st.session_state.active_model}`")

if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Study": show_study()
    
