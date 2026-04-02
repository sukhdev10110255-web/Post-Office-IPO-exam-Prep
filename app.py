import streamlit as st
import os

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v24.1", layout="wide", initial_sidebar_state="collapsed")

# --- UI Styling ---
def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme', 'Light') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme', 'Light') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-size: 30px; color: #ff4b4b; padding: 10px; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; }}
        .result-card {{ padding: 20px; background-color: #d4edda; color: #155724; border-radius: 10px; text-align: center; font-size: 22px; font-weight: bold; border: 2px solid #c3e6cb; }}
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
        "score": 0,
        "user_answers": {}
    })

# ================= SYLLABUS DATA (2025 Updates) =================
SYLLABUS = {
    "Paper 1": ["Post Office Act 2023", "Post Office Rules 2024", "PO Guide Part I", "POSB Manual", "IT Modernization 2.0"],
    "Paper 2": ["Noting (15 Marks)", "Drafting (15 Marks)", "Major Penalty Charge Sheet (20 Marks)"],
    "Paper 3": ["Constitution of India", "BNSS 2023", "CAT Act 1985", "RTI Act 2005", "Ethics & Reasoning"]
}

# ================= EXAM QUESTIONS (From Paper-IV 2024) =================
# Source: IPO Exam 2024 Question Paper IV
OFFICIAL_EXAM = [
    {"q": "Select the synonym for 'Flummox'", "opt": ["Baffle", "Elevate", "Praise", "Immerse"], "ans": "Baffle"},
    {"q": "Select the antonym for 'Paucity'", "opt": ["Dearth", "Abundance", "Exigency", "Sparsity"], "ans": "Abundance"},
    {"q": "What is the meaning of the idiom 'To be in two minds'?", "opt": ["Over confident", "Less effective", "In dilemma", "None"], "ans": "In dilemma"},
    {"q": "Which country will host the 9th edition of ICC Women's T20 World Cup?", "opt": ["England", "Bangladesh", "Australia", "India"], "ans": "Bangladesh"},
    {"q": "Who is the Ex-Officio Chairperson of Rajya Sabha?", "opt": ["Governor", "Prime Minister", "President", "Vice President"], "ans": "Vice President"}
]

# ================= PAGES =================

def show_home():
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    if col1.button("Paper 1"): navigate_to("Paper", "Paper 1")
    if col2.button("Paper 2"): navigate_to("Paper", "Paper 2")
    if col3.button("Paper 3"): navigate_to("Paper", "Paper 3")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Prepare {paper}</h1>", unsafe_allow_html=True)
    
    st.write("### 📋 Syllabus Topics")
    for topic in SYLLABUS.get(paper, []):
        st.markdown(f"- **{topic}**")
    
    st.divider()
    col_back, col_exam = st.columns(2)
    if col_back.button("⬅️ Back to Home"): navigate_to("Home")
    if col_exam.button("📝 Take Live Exam"): navigate_to("Exam")

def show_exam():
    st.markdown(f"<h1 class='header-text'>{st.session_state.selected_paper} - Mock Test</h1>", unsafe_allow_html=True)
    
    if not st.session_state.test_submitted:
        with st.form("live_test"):
            for i, item in enumerate(OFFICIAL_EXAM):
                st.write(f"**Q{i+1}: {item['q']}**")
                st.session_state.user_answers[i] = st.radio("Choose:", item['opt'], key=f"exam_q_{i}")
            
            if st.form_submit_button("Submit Exam"):
                score = 0
                for i, item in enumerate(OFFICIAL_EXAM):
                    if st.session_state.user_answers[i] == item['ans']:
                        score += 1
                st.session_state.score = score
                st.session_state.test_submitted = True
                st.rerun()
    else:
        st.markdown(f"<div class='result-card'>🎯 Result: {st.session_state.score} / {len(OFFICIAL_EXAM)} Correct!</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🔄 Retake Exam"):
            st.session_state.test_submitted = False
            st.rerun()
        if c2.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def navigate_to(page, data=None):
    st.session_state.page = page
    if data: st.session_state.selected_paper = data
    st.rerun()

# ================= MAIN ROUTER =================
apply_android_style()
if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Exam": show_exam()
    
