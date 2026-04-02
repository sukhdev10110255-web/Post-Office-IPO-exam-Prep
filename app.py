import streamlit as st
import os
import pandas as pd
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG & THEME =================
st.set_page_config(page_title="Avyan LDCE v25.0", layout="wide", initial_sidebar_state="collapsed")

def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-size: 32px; color: #ff4b4b; padding: 10px; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; border: 1px solid #ccc; }}
        .weak-box {{ background-color: #ffebee; border-left: 5px solid #f44336; padding: 10px; border-radius: 5px; color: #b71c1c; margin-bottom: 5px; }}
        </style>
    """, unsafe_allow_html=True)

# ================= STATE MANAGEMENT (History & Weak Points) =================
if "page" not in st.session_state:
    st.session_state.update({
        "page": "Home",
        "theme": "Light",
        "lang": "Bilingual",
        "selected_paper": None,
        "selected_topic": None,
        "exam_history": [], # List of scores
        "weak_topics": set(), # Topics where user failed questions
        "writing_content": ""
    })

# ================= SYLLABUS & EXAM DATA =================
SYLLABUS_2025 = {
    "Paper 1": ["Post Office Act 2023", "Post Office Rules 2024", "PO Guide Part I & II", "POSB Manual", "IT Modernization 2.0"],
    "Paper 2": ["Noting (15 Marks)", "Drafting (15 Marks)", "Major Penalty Charge Sheet (20 Marks)"],
    "Paper 3": ["Constitution of India", "BNSS 2023", "CAT Act 1985", "RTI Act 2005", "Ethics & Reasoning"]
}

# Real Questions from your 2024 Paper-IV
OFFICIAL_EXAM = [
    {"q": "Synonym for 'Flummox'?", "opt": ["Baffle", "Elevate", "Praise", "Immerse"], "ans": "Baffle", "topic": "English Language"},
    {"q": "Ex-Officio Chairperson of Rajya Sabha?", "opt": ["Governor", "Prime Minister", "President", "Vice President"], "ans": "Vice President", "topic": "Constitution of India"},
    {"q": "9th edition of ICC Women's T20 World Cup Host?", "opt": ["England", "Bangladesh", "Australia", "India"], "ans": "Bangladesh", "topic": "General Knowledge"},
    {"q": "Richard is afraid ____ spiders.", "opt": ["off", "of", "from", "in"], "ans": "of", "topic": "English Language"}
]

# ================= AI ENGINE =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    client = Cerebras(api_key=api_key)
    for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[{"role":"user", "content": f"In {st.session_state.lang}: {prompt}"}],
                max_tokens=1500
            )
            return res.choices[0].message.content
        except: continue
    return "⚠️ AI Connection Fail."

# ================= PAGES =================

def show_home():
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Paper 1"): navigate_to("Paper", "Paper 1")
    if c2.button("Paper 2"): navigate_to("Paper", "Paper 2")
    if c3.button("Paper 3"): navigate_to("Paper", "Paper 3")
    
    st.divider()
    st.subheader("📊 Your Performance History")
    if st.session_state.exam_history:
        st.line_chart(st.session_state.exam_history)
    else:
        st.info("No exam history yet. Take a test to see progress!")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Prepare {paper}</h1>", unsafe_allow_html=True)
    
    col_study, col_rev = st.columns([2, 1])
    with col_study:
        st.write("### 📘 Syllabus Topics")
        for topic in SYLLABUS_2025.get(paper, []):
            if st.button(f"📌 {topic}", key=f"btn_{topic}"):
                navigate_to("Study", topic)
    
    with col_rev:
        st.write("### 🧠 Smart Revision")
        if st.session_state.weak_topics:
            st.error("Weak Topics Identified:")
            for wt in st.session_state.weak_topics:
                if st.button(f"🔄 Revise {wt}", key=f"rev_{wt}"):
                    navigate_to("Study", wt)
        else:
            st.success("No weak points yet! Excellent.")

    st.divider()
    c_b, c_e = st.columns(2)
    if c_b.button("⬅️ Back Home"): navigate_to("Home")
    if c_e.button("📝 Take Live Exam"): navigate_to("Exam")

def show_exam():
    st.markdown("<h1 class='header-text'>Live Exam Mode</h1>", unsafe_allow_html=True)
    with st.form("exam_form"):
        user_ans = {}
        for i, item in enumerate(OFFICIAL_EXAM):
            st.write(f"**Q{i+1}: {item['q']}**")
            user_ans[i] = st.radio("Select:", item['opt'], key=f"q_{i}")
        
        if st.form_submit_button("Submit & Save Result"):
            correct_count = 0
            for i, item in enumerate(OFFICIAL_EXAM):
                if user_ans[i] == item['ans']:
                    correct_count += 1
                else:
                    st.session_state.weak_topics.add(item['topic']) # ऑटो Weak Point ट्रैकिंग
            
            st.session_state.exam_history.append(correct_count)
            st.success(f"Exam Submitted! Your Score: {correct_count}/{len(OFFICIAL_EXAM)}")
            time.sleep(2)
            navigate_to("Paper", st.session_state.selected_paper)

def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📖 AI Notes", "💬 AI Discussion"])
    with tab1:
        if st.button("✨ Generate Notes"):
            st.markdown(call_ai(f"Provide detailed notes for {topic}"))
    with tab2:
        query = st.chat_input("Ask AI...")
        if query: st.write(call_ai(query))

    if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def navigate_to(page, data=None):
    st.session_state.page = page
    if data:
        if page == "Paper": st.session_state.selected_paper = data
        if page == "Study": st.session_state.selected_topic = data
    st.rerun()

# ================= ROUTER =================
apply_android_style()
if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Study": show_study()
elif st.session_state.page == "Exam": show_exam()
    
