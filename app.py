import streamlit as st
import os
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v24.3", layout="wide", initial_sidebar_state="collapsed")

def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-size: 32px; color: #ff4b4b; padding: 10px; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; border: 1px solid #ccc; }}
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
        "active_model": "None"
    })

# ================= FULL SYLLABUS (Aug 2025 Order) =================
SYLLABUS_2025 = {
    "Paper 1": [
        "The Post Office Act, 2023", "The Post Office Rules, 2024", "PO Guide Part I & II", 
        "Government Savings Promotion Act 1873", "Prevention of Money Laundering Act 2002", 
        "Consumer Protection Act 2019", "Information Technology Act 2000",
        "POSB Manual Vol I, II & III", "SANKALAN (PLI Rules)", "CCS Conduct Rules 1964", 
        "CCS CCA Rules 1965", "GDS Rules 2020", "IT Modernization 2.0 (APT Knowledge)", 
        "DIGIPIN Basic Understanding", "Dak Ghar Niryat Kendra (DNKs)"
    ],
    "Paper 2": [
        "Noting (Approx 200 words)", 
        "Drafting (Approx 200 words)", 
        "Draft Major Penalty Charge Sheet"
    ],
    "Paper 3": [
        "Constitution of India (Fundamental Rights/Duties)", 
        "The Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)", 
        "Central Administrative Tribunal Act, 1985", "RTI Act, 2005", 
        "Manuals on Procurement", "CCS Pension Rules 2021", 
        "CCS GPF Rules 1961", "GFR 2017 (Chapter 2 & 6)", "FHB Volume I & II", 
        "English Language", "General Knowledge & Current Affairs",
        "Reasoning & Quantitative Aptitude"
    ]
}

# ================= UNIVERSAL AI ENGINE (Model Fix) =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key: return "❌ CEREBRAS_API_KEY missing in Render."
    
    client = Cerebras(api_key=api_key)
    # Trying all known working names on Cerebras
    models_to_test = [
        "llama-3.3-70b-versatile", 
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3.1-70b",
        "llama3.1-8b"
    ]
    
    for model_name in models_to_test:
        try:
            res = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": "You are an expert LDCE IP Tutor."},
                          {"role": "user", "content": f"In {st.session_state.lang}: {prompt}"}],
                max_tokens=1500
            )
            st.session_state.active_model = model_name
            return res.choices[0].message.content
        except Exception:
            continue
            
    return "⚠️ AI Connectivity Fail: All models failed. Please verify your API Key."

# ================= PAGES =================

def show_home():
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    st.divider()
    c1, c2, c3 = st.columns(3)
    if c1.button("Paper 1 (250m)"): navigate_to("Paper", "Paper 1")
    if c2.button("Paper 2 (50m)"): navigate_to("Paper", "Paper 2")
    if c3.button("Paper 3 (300m)"): navigate_to("Paper", "Paper 3")
    
    with st.sidebar:
        st.selectbox("Theme", ["Light", "Dark"], key="theme")
        st.selectbox("Language", ["Bilingual", "Hindi", "English"], key="lang")
        st.caption(f"Active Model: {st.session_state.active_model}")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Prepare {paper}</h1>", unsafe_allow_html=True)
    st.write(f"### Click a topic to study ({paper}):")
    
    cols = st.columns(2)
    for i, topic in enumerate(SYLLABUS_2025.get(paper, [])):
        if cols[i%2].button(f"📘 {topic}"):
            navigate_to("Study", topic)

    st.divider()
    col_back, col_exam = st.columns(2)
    if col_back.button("⬅️ Back to Home"): navigate_to("Home")
    if col_exam.button("📝 Take Live Exam"): st.info("Exam System Initializing...")

def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📖 AI Notes", "💬 AI Discussion", "📝 MCQ Practice"])
    
    with tab1:
        if st.button("✨ Generate Detailed Notes"):
            with st.spinner("Connecting to AI..."):
                st.markdown(call_ai(f"Provide professional notes on '{topic}' for LDCE IP Exam."))
    
    with tab2:
        q = st.chat_input("Ask a doubt...")
        if q: st.write(call_ai(f"Topic: {topic}. Query: {q}"))
        
    with tab3:
        if st.button("Generate MCQs"):
            st.markdown(call_ai(f"Generate 5 MCQs on {topic}."))

    if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def navigate_to(page, data=None):
    st.session_state.page = page
    if page == "Paper": st.session_state.selected_paper = data
    if page == "Study": st.session_state.selected_topic = data
    st.rerun()

# ================= ROUTER =================
apply_android_style()
if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Study": show_study()
    
