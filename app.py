import streamlit as st
import os
import time
from cerebras.cloud.sdk import Cerebras

# ================= 1. CONFIG =================
st.set_page_config(page_title="Avyan LDCE v26.1", layout="wide", initial_sidebar_state="collapsed")

def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-size: 30px; color: #ff4b4b; padding: 10px; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; border: 1px solid #ccc; }}
        .timer-text {{ text-align: center; font-size: 24px; font-weight: bold; color: #d32f2f; background: #fff; padding: 10px; border-radius: 10px; border: 2px solid #ff4b4b; }}
        /* MCQ Clickable Area Fix */
        .stRadio > div {{ background: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }}
        </style>
    """, unsafe_allow_html=True)

# ================= 2. STATE MANAGEMENT =================
if "page" not in st.session_state:
    st.session_state.update({
        "page": "Home",
        "theme": "Light",
        "lang": "Bilingual",
        "selected_paper": None,
        "selected_topic": None,
        "exam_active": False,
        "test_submitted": False,
        "exam_start_time": 0,
        "score": 0,
        "weak_topics": set(),
        "exam_history": []
    })

# ================= 3. UPDATED SYLLABUS (Aug 2025) =================
SYLLABUS_2025 = {
    "Paper 1": ["Post Office Act 2023", "Post Office Rules 2024", "PO Guide Part I & II", "POSB Manual", "IT Modernization 2.0"],
    "Paper 2": ["Noting (15 Marks)", "Drafting (15 Marks)", "Major Penalty Charge Sheet (Rule 14)"],
    "Paper 3": ["Constitution of India", "BNSS 2023", "CAT Act 1985", "RTI Act 2005", "Ethics & Reasoning"]
[span_4](start_span)[span_5](start_span)[span_6](start_span)}

# Official 2024 Questions for Exam Mode
OFFICIAL_EXAM = [
    {"q": "Synonym for 'Flummox'?", "opt": ["Baffle", "Elevate", "Praise", "Immerse"], "ans": "Baffle", "topic": "English Language"},
    {"q": "Who is the Ex-Officio Chairperson of Rajya Sabha?", "opt": ["Governor", "Prime Minister", "President", "Vice President"], "ans": "Vice President", "topic": "Constitution of India"},
    {"q": "In Water polo, how many players play in each side?", "opt": ["9", "11", "8", "7"], "ans": "7", "topic": "General Knowledge"}
][span_4](end_span)[span_5](end_span)[span_6](end_span)

# ================= 4. AI ENGINE (Failover) =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    client = Cerebras(api_key=api_key)
    for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            res = client.chat.completions.create(model=model, messages=[{"role":"user","content":prompt}], max_tokens=1500)
            return res.choices[0].message.content
        except: continue
    return "AI connectivity failed."

# ================= 5. PAGES =================

def show_home():
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Paper 1 (250m)"): navigate_to("Paper", "Paper 1")
    if c2.button("Paper 2 (50m)"): navigate_to("Paper", "Paper 2")
    if c3.button("Paper 3 (300m)"): navigate_to("Paper", "Paper 3")
    
    st.divider()
    st.subheader("📊 Performance Tracker")
    if st.session_state.exam_history: st.line_chart(st.session_state.exam_history)

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>{paper} Syllabus</h1>", unsafe_allow_html=True)
    for topic in SYLLABUS_2025.get(paper, []):
        if st.button(f"📌 {topic}"): navigate_to("Study", topic)
    
    st.divider()
    c_b, c_e = st.columns(2)
    if c_b.button("⬅️ Back Home"): navigate_to("Home")
    if c_e.button("📝 Start Live Exam (Timed)"): 
        st.session_state.exam_active = True
        st.session_state.test_submitted = False
        st.session_state.exam_start_time = time.time()
        navigate_to("Exam")

def show_exam():
    # EXAM TIMER LOGIC
    [span_7](start_span)total_time = 150 * 60 # 2.5 Hours in seconds[span_7](end_span)
    elapsed = time.time() - st.session_state.exam_start_time
    remaining = total_time - elapsed
    
    if remaining <= 0:
        st.error("Time Up! Submit your exam now.")
        remaining = 0
    
    mins, secs = divmod(int(remaining), 60)
    st.markdown(f"<div class='timer-text'>⏱️ Countdown: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
    
    if not st.session_state.test_submitted:
        with st.form("exam_form"):
            user_ans = {}
            for i, item in enumerate(OFFICIAL_EXAM):
                st.write(f"**Q{i+1}: {item['q']}**")
                # CLICKABLE RADIO BUTTONS
                user_ans[i] = st.radio("Select Response:", item['opt'], key=f"ex_{i}")
            
            if st.form_submit_button("Submit Final Exam"):
                score = sum(1 for i, item in enumerate(OFFICIAL_EXAM) if user_ans[i] == item['ans'])
                st.session_state.score = score
                st.session_state.exam_history.append(score)
                st.session_state.test_submitted = True
                st.rerun()
    else:
        st.success(f"Exam Submitted! Result: {st.session_state.score} / {len(OFFICIAL_EXAM)}")
        if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    if st.button("📖 Generate Study Notes"):
        st.markdown(call_ai(f"Notes for {topic} in {st.session_state.lang}"))
    if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def navigate_to(page, data=None):
    st.session_state.page = page
    if page == "Paper": st.session_state.selected_paper = data
    if page == "Study": st.session_state.selected_topic = data
    st.rerun()

# ================= 6. ROUTER =================
apply_android_style()
if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Study": show_study()
elif st.session_state.page == "Exam": show_exam()
            
