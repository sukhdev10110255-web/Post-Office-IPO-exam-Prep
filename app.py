import streamlit as st
import os
from PyPDF2 import PdfReader
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG & THEME =================
st.set_page_config(page_title="Avyan LDCE App", layout="wide", initial_sidebar_state="collapsed")

# --- UI Styling (Android App Look) ---
def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-family: 'sans-serif'; font-size: 38px; padding: 20px; }}
        .stButton>button {{ width: 100%; border-radius: 15px; height: 3.8em; font-weight: bold; border: 1px solid #ccc; }}
        .stTextInput>div>div>input {{ border-radius: 25px; padding: 15px; }}
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

# ================= SYLLABUS DATA =================
SYLLABUS = {
    "Paper 1": ["PO Guide Part I", "PO Guide Part II", "POSB Manual Vol I", "PLI/RPLI Rules 2024", "IT Modernization 2.0"],
    "Paper 2": ["Postal Manual Vol V", "Postal Manual Vol VI", "Postal Manual Vol VII", "FHB Vol I", "CCS Conduct Rules 1964"],
    "Paper 3": ["Indian Constitution", "Central Administrative Tribunal Act 1985", "RTI Act 2005", "Arithmetic", "Reasoning"]
}

# ================= AI ENGINE =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    client = Cerebras(api_key=api_key)
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":f"In {st.session_state.lang}: {prompt}"}],
            max_tokens=1500
        )
        return res.choices[0].message.content
    except:
        return "⚠️ AI Error. Please check API Key/Connection."

# ================= PAGES =================

# --- PAGE 1: HOME ---
def show_home():
    # Top Right Controls (Columns for fixed alignment)
    col_empty, col_ctrl = st.columns([4, 1])
    with col_ctrl:
        st.session_state.theme = st.selectbox("🎨 Theme", ["Light", "Dark"])
        st.session_state.lang = st.selectbox("🌐 Language", ["Bilingual", "Hindi", "English"])
    
    # Middle Content
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    
    # Search Section
    c_l, c_mid, c_r = st.columns([1, 2, 1])
    with c_mid:
        search_q = st.text_input("🔍 Search Topic", placeholder="Enter topic to search online...")
        # FIX: Selectbox doesn't have horizontal, using columns instead
        col_eng1, col_eng2, col_eng3 = st.columns(3)
        if col_eng1.button("Google"): st.markdown(f"[Searching...](https://www.google.com/search?q={search_q})")
        if col_eng2.button("Bing"): st.markdown(f"[Searching...](https://www.bing.com/search?q={search_q})")
        if col_eng3.button("D-Go"): st.markdown(f"[Searching...](https://duckduckgo.com/?q={search_q})")
        
        st.divider()
        st.subheader("Choose Your Exam Paper")
        p1, p2, p3 = st.columns(3)
        if p1.button("Paper 1"): navigate_to("Paper", "Paper 1")
        if p2.button("Paper 2"): navigate_to("Paper", "Paper 2")
        if p3.button("Paper 3"): navigate_to("Paper", "Paper 3")

# --- PAGE 2: PAPER SYLLABUS ---
def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Let's Prepare {paper}</h1>", unsafe_allow_html=True)
    
    # Updated Clickable Syllabus
    st.write("### 📋 Updated Syllabus")
    cols = st.columns(2)
    for i, topic in enumerate(SYLLABUS[paper]):
        if cols[i%2].button(f"📌 {topic}"):
            navigate_to("Study", topic)

    st.divider()
    b1, b2, b3 = st.columns(3)
    b1.button("📝 Give Exam")
    b2.button("📊 Results")
    b3.button("🧠 Revision")
    
    if st.button("⬅️ Back to Home"): navigate_to("Home")

# --- PAGE 3: STUDY TOPIC ---
def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    # Attached PDF Document
    with st.expander("📂 Attached PDF Document (Click to Open)"):
        pdf_file = st.file_uploader("Upload PDF Reference", type="pdf")
        if pdf_file: st.success(f"Context for {topic} loaded.")

    # Functional Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📖 AI Notes", "💬 AI Discussion", "📝 MCQ Test", "📉 Weak Point"])
    
    with tab1:
        if st.button("✨ Generate Short Notes"):
            with st.spinner("AI Generating..."):
                st.markdown(call_ai(f"Detailed short notes for {topic}"))
    
    with tab2:
        query = st.chat_input("Ask AI Discussion...")
        if query: st.write(call_ai(f"Topic {topic}: {query}"))
        
    with tab3:
        if st.button("Start MCQ Test"):
            st.markdown(call_ai(f"Generate 5 MCQs on {topic}"))
            
    with tab4:
        st.info("Performance tracking coming soon to Android App...")

    if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

# --- NAVIGATION HELPER ---
def navigate_to(page, data=None):
    st.session_state.page = page
    if data:
        if page == "Paper": st.session_state.selected_paper = data
        if page == "Study": st.session_state.selected_topic = data
    st.rerun()

# ================= APP ROUTER =================
apply_android_style()
if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Study": show_study()
    
