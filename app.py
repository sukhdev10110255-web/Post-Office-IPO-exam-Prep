import streamlit as st
import os
import time
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v24.0", layout="wide", initial_sidebar_state="collapsed")

# --- UI Styling ---
def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-size: 30px; color: #ff4b4b; padding: 10px; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; }}
        .result-card {{ padding: 20px; background-color: #d4edda; color: #155724; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

# ================= SESSION STATE =================
if "page" not in st.session_state:
    st.session_state.update({
        "page": "Home",
        "theme": "Light",
        "lang": "Bilingual",
        "selected_paper": None,
        "test_submitted": False,
        "score": 0
    })

# ================= TEST QUESTIONS (Based on your 2024 PDF) =================
[span_0](start_span)#
OFFICIAL_QUESTIONS = [
    {"q": "What is the synonym of 'Flummox'?", "opt": ["Baffle", "Elevate", "Praise", "Immerse"], "ans": "Baffle"},
    {"q": "Antonym of 'Paucity'?", "opt": ["Dearth", "Abundance", "Exigency", "Sparsity"], "ans": "Abundance"},
    {"q": "Meaning of idiom 'To be in two minds'?", "opt": ["Over confident", "Less effective", "In dilemma", "None"], "ans": "In dilemma"},
    {"q": "Richard is afraid ____ spiders.", "opt": ["off", "of", "from", "in"], "ans": "of"},
    {"q": "Which country will host 9th edition of ICC Women's T20 World Cup?", "opt": ["England", "Bangladesh", "Australia", "India"], "ans": "Bangladesh"}
]

# ================= AI ENGINE =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    client = Cerebras(api_key=api_key)
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user", "content": f"Lang: {st.session_state.lang}. Prompt: {prompt}"}],
            max_tokens=1000
        )
        return res.choices[0].message.content
    except: return "AI Connection Error."

# ================= PAGES =================

def show_home():
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Paper 1"): navigate_to("Paper", "Paper 1")
    if c2.button("Paper 2"): navigate_to("Paper", "Paper 2")
    if c3.button("Paper 3"): navigate_to("Paper", "Paper 3")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Prepare {paper}</h1>", unsafe_allow_html=True)
    st.info(f"Syllabus for {paper} is loaded below.")
    
    # Bottom Buttons as requested
    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back to Home"): navigate_to("Home")
    if col2.button("📝 Take Live Exam"): navigate_to("Exam")

def show_exam():
    st.markdown(f"<h1 class='header-text'>{st.session_state.selected_paper} - Mock Test</h1>", unsafe_allow_html=True)
    
    if not st.session_state.test_submitted:
        with st.form("exam_form"):
            user_responses = {}
            for i, item in enumerate(OFFICIAL_QUESTIONS):
                st.write(f"**Q{i+1}: {item['q']}**")
                user_responses[i] = st.radio("Choose answer:", item['opt'], key=f"q{i}")
            
            if st.form_submit_button("Submit Exam"):
                score = sum(1 for i, item in enumerate(OFFICIAL_QUESTIONS) if user_responses[i] == item['ans'])
                st.session_state.score = score
                st.session_state.test_submitted = True
                st.rerun()
    else:
        # Result Display
        st.markdown(f"<div class='result-card'>🎯 Your Score: {st.session_state.score} / {len(OFFICIAL_QUESTIONS)}</div>", unsafe_allow_html=True)
        if st.button("🔄 Retake Exam"):
            st.session_state.test_submitted = False
            st.rerun()
        if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def navigate_to(page, data=None):
    st.session_state.page = page
    if data: st.session_state.selected_paper = data
    st.rerun()

# ================= MAIN =================
apply_android_style()
if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Exam": show_exam()
    
