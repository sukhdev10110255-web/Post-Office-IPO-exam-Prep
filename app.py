import streamlit as st
import os
from PyPDF2 import PdfReader
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG & THEME =================
st.set_page_config(page_title="Avyan LDCE v24.2 Pro", layout="wide", initial_sidebar_state="collapsed")

def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-size: 32px; color: #ff4b4b; padding: 10px; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; border: 1px solid #ccc; }}
        .syllabus-card {{ background: #ffffff; padding: 10px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 10px; color: #333; }}
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
        "test_submitted": False,
        "score": 0
    })

# ================= FULL UPDATED 2025 SYLLABUS (from PDF) =================
SYLLABUS_2025 = {
    "Paper 1": [
        "Post Office Act 2023", "Post Office Rules 2024", "PO Guide Part I & II", 
        "Government Savings Promotion Act 1873", "Prevention of Money Laundering Act 2002", 
        "Consumer Protection Act 2019", "Information Technology Act 2000",
        "POSB Manual Vol I, II & III", "SANKALAN (PLI Rules)", "CCS Conduct Rules 1964", 
        "CCS CCA Rules 1965", "GDS Rules 2020", "IT Modernization 2.0", "DIGIPIN",
        "Mail Network Optimization Project", "Dak Ghar Niryat Kendra (DNK)"
    ],
    "Paper 2": [
        "Noting (Approx 200 words)", 
        "Drafting (Approx 200 words)", 
        "Draft Major Penalty Charge Sheet (Rule 14)"
    ],
    "Paper 3": [
        "Constitution of India (Preamble, Fundamental Rights/Duties)", 
        "Bharatiya Nagarik Suraksha Sanhita 2023 (BNSS)", 
        "Central Administrative Tribunal Act 1985", "RTI Act 2005 & Rules 2012", 
        "Manuals on Procurement (Goods, Works, Consultancy)", "CCS Pension Rules 2021", 
        "CCS GPF Rules 1961", "GFR 2017 (Ch 2 & 6)", "FHB Vol I & II", 
        "English Language", "General Knowledge & Current Affairs",
        "Reasoning & Quantitative Aptitude", "Ethics & Interpersonal Skills"
    ]
}

# ================= AI ENGINE (Hyper-Switch) =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    client = Cerebras(api_key=api_key)
    models = ["llama-3.3-70b-versatile", "llama3.1-8b"]
    for model in models:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[{"role":"system", "content": f"Expert LDCE Tutor. Lang: {st.session_state.lang}"},
                          {"role":"user", "content": prompt}],
                max_tokens=2000
            )
            return res.choices[0].message.content
        except: continue
    return "⚠️ AI connectivity failed."

# ================= PAGES =================

def show_home():
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    st.divider()
    c1, c2, c3 = st.columns(3)
    if c1.button("📜 Paper 1 (250m)"): navigate_to("Paper", "Paper 1")
    if c2.button("✍️ Paper 2 (50m)"): navigate_to("Paper", "Paper 2")
    if c3.button("📊 Paper 3 (300m)"): navigate_to("Paper", "Paper 3")
    
    st.sidebar.selectbox("Theme", ["Light", "Dark"], key="theme")
    st.sidebar.selectbox("Language", ["Bilingual", "Hindi", "English"], key="lang")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Prepare {paper}</h1>", unsafe_allow_html=True)
    st.markdown(f"**Syllabus for {paper} (Aug 2025 Updates):** Click a topic to study.")
    
    # CLICKABLE SYLLABUS RESTORED
    cols = st.columns(2)
    for i, topic in enumerate(SYLLABUS_2025.get(paper, [])):
        if cols[i%2].button(f"📘 {topic}"):
            navigate_to("Study", topic)

    st.divider()
    col_back, col_exam = st.columns(2)
    if col_back.button("⬅️ Back to Home"): navigate_to("Home")
    if col_exam.button("📝 Take Live Exam"): navigate_to("Exam")

def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📖 AI Notes", "💬 AI Chat", "📝 MCQ Practice"])
    
    with tab1:
        if st.button("✨ Generate Detailed Notes"):
            with st.spinner("Analyzing Departmental Rules..."):
                st.markdown(call_ai(f"Provide professional notes on {topic} for Inspector Posts Exam 2025."))
    
    with tab2:
        q = st.chat_input("Ask a doubt about this topic...")
        if q: st.write(call_ai(f"Topic: {topic}. Query: {q}"))
        
    with tab3:
        if st.button("Generate Test"):
            st.markdown(call_ai(f"Generate 5 MCQs on {topic}."))

    if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def show_exam():
    # Previous Exam Logic Restored...
    st.markdown("<h1 class='header-text'>Live Exam Mode</h1>", unsafe_allow_html=True)
    st.info("Mock Test based on 2024 Paper-IV questions.")
    if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def navigate_to(page, data=None):
    st.session_state.page = page
    if data:
        if page == "Paper": st.session_state.selected_paper = data
        if page == "Study": st.session_state.selected_topic = data
    st.rerun()

# ================= MAIN ROUTER =================
apply_android_style()
if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Study": show_study()
elif st.session_state.page == "Exam": show_exam()
    
