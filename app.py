import streamlit as st
import os
from PyPDF2 import PdfReader
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG & THEME =================
st.set_page_config(page_title="Avyan LDCE v23.1 Pro", layout="wide", initial_sidebar_state="collapsed")

def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-family: 'sans-serif'; font-size: 32px; padding: 10px; color: #ff4b4b; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; border: 1px solid #ccc; }}
        .syllabus-box {{ background: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #ff4b4b; color: #333; margin-bottom: 20px; }}
        .format-card {{ background: #e3f2fd; padding: 15px; border-radius: 10px; border: 1px dashed #1565c0; color: #0d47a1; font-family: 'monospace'; }}
        </style>
    """, unsafe_allow_html=True)

# ================= STATE MANAGEMENT =================
if "page" not in st.session_state:
    st.session_state.update({
        "page": "Home",
        "theme": "Light",
        "lang": "Bilingual",
        "selected_paper": None,
        "selected_topic": None
    })

# ================= LATEST 2025 SYLLABUS (Aug 22, 2025) =================
SYLLABUS_2025 = {
    "Paper 1": [
        "Post Office Act 2023", "Post Office Rules 2024", "PO Guide Part I & II", 
        "POSB Manual Vol I, II & III", "SANKALAN (PLI Rules)", "CCS Conduct Rules 1964", 
        "CCS CCA Rules 1965", "GDS Rules 2020", "IT Modernization 2.0", "DIGIPIN"
    ],
    "Paper 2": [
        "Noting (Approx 200 words)", 
        "Drafting (Approx 200 words)", 
        "Draft Major Penalty Charge Sheet (Rule 14)"
    ],
    "Paper 3": [
        "Constitution of India", "BNSS 2023 (Bharatiya Nagarik Suraksha Sanhita)", 
        "CAT Act 1985", "RTI Act 2005", "CCS Pension Rules 2021", 
        "GFR 2017", "FHB Vol I & II", "English & Reasoning", "Ethics"
    ]
}

# ================= HYPER-SWITCH AI ENGINE =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    client = Cerebras(api_key=api_key)
    models = ["llama-3.3-70b-versatile", "llama3.1-8b"]
    for model in models:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[{"role":"system", "content": f"You are an IP Exam Expert. Lang: {st.session_state.lang}"},
                          {"role":"user", "content": prompt}],
                max_tokens=2000
            )
            return res.choices[0].message.content
        except: continue
    return "⚠️ AI Connectivity Issue."

# ================= APP PAGES =================

def show_home():
    col_l, col_r = st.columns([3, 1])
    with col_r:
        st.session_state.theme = st.selectbox("🎨 Theme", ["Light", "Dark"])
        st.session_state.lang = st.selectbox("🌐 Language", ["Bilingual", "Hindi", "English"])
    
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    
    m_l, m_c, m_r = st.columns([1, 2, 1])
    with m_c:
        st.subheader("Choose Your Exam Paper (New Pattern)")
        p1, p2, p3 = st.columns(3)
        if p1.button("Paper 1 (250m)"): navigate_to("Paper", "Paper 1")
        if p2.button("Paper 2 (50m)"): navigate_to("Paper", "Paper 2")
        if p3.button("Paper 3 (300m)"): navigate_to("Paper", "Paper 3")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Let's Prepare {paper}</h1>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='syllabus-box'><b>{paper} Syllabus:</b> Select a topic to study.</div>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, topic in enumerate(SYLLABUS_2025[paper]):
        if cols[i%2].button(f"📘 {topic}"):
            navigate_to("Study", topic)
    
    st.divider()
    if st.button("⬅️ Back to Home"): navigate_to("Home")

def show_study():
    topic = st.session_state.selected_topic
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📖 Study Material", "💬 AI Discussion", "📝 Practice Test"])
    
    with tab1:
        if paper == "Paper 2":
            st.info("💡 Paper 2 requires specific formats. Click below for a solved Master Template.")
            if st.button("✨ Generate Solved Format & Example"):
                with st.spinner("Drafting professional content..."):
                    prompt = f"Provide the official departmental format and a solved 2025 example for: {topic}. Include standard 'Note' or 'Draft' styles as per Postal Manual Vol II."
                    st.markdown(call_ai(prompt))
        else:
            if st.button("✨ Generate Pro Notes"):
                with st.spinner("Analyzing rules..."):
                    st.markdown(call_ai(f"Explain {topic} in detail for IP Exam."))
    
    with tab2:
        query = st.chat_input("Ask any doubt...")
        if query: st.write(call_ai(f"Regarding {topic}: {query}"))
        
    with tab3:
        if st.button("Start MCQ/Practice Quiz"):
            st.markdown(call_ai(f"Generate practice questions for {topic}"))

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
    
