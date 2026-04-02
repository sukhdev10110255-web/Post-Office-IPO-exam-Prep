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
        .header-text {{ text-align: center; font-weight: bold; font-family: 'sans-serif'; }}
        .stButton>button {{ width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; border: 1px solid #ddd; }}
        .topic-card {{ padding: 15px; border-radius: 10px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); color: black; cursor: pointer; margin-bottom: 10px; }}
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
        "results": [],
        "weak_points": []
    })

# ================= SYLLABUS DATA (Updated 3 Papers) =================
SYLLABUS = {
    "Paper 1": ["PO Guide Part I", "PO Guide Part II", "POSB Manual Vol I", "POSB Manual Vol II", "POSB Manual Vol III", "PLI/RPLI Rules 2024", "IT Modernization Project 2.0"],
    "Paper 2": ["Postal Manual Vol V", "Postal Manual Vol VI (Part I, II, III)", "Postal Manual Vol VII", "FHB Vol I", "FHB Vol II", "CCS Conduct Rules 1964", "CCS CCA Rules 1965"],
    "Paper 3": ["Indian Constitution", "Central Administrative Tribunal Act 1985", "RTI Act 2005", "Consumer Protection Act", "Indian Economy", "General Intelligence & Reasoning", "Arithmetic"]
}

# ================= AI ENGINE =================
def call_ai(prompt):
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b"]
    api_key = os.getenv("CEREBRAS_API_KEY")
    client = Cerebras(api_key=api_key)
    for m in models:
        try:
            res = client.chat.completions.create(model=m, messages=[{"role":"user","content":prompt}], max_tokens=1500)
            return res.choices[0].message.content
        except: continue
    return "⚠️ Connection Error. Check API Key."

# ================= PAGES =================

# --- PAGE 1: HOME ---
def show_home():
    # Top Right Controls
    col_l, col_c, col_r = st.columns([1,2,1])
    with col_r:
        st.session_state.theme = st.selectbox("Theme", ["Light", "Dark"], label_visibility="collapsed")
        st.session_state.lang = st.selectbox("Language", ["Bilingual", "Hindi", "English"], label_visibility="collapsed")
    
    with col_c:
        st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
        # Search Bar
        search_q = st.text_input("🔍 Search Topic", placeholder="Enter topic to search online...")
        engine = st.selectbox("Engine", ["Google", "Bing", "DuckDuckGo"], horizontal=True)
        if search_q:
            st.markdown(f"[Click to Search Online](https://www.google.com/search?q={search_q})")
        
        st.divider()
        st.subheader("Choose Your Exam Paper")
        c1, c2, c3 = st.columns(3)
        if c1.button("Paper 1"): navigate_to("Paper", "Paper 1")
        if c2.button("Paper 2"): navigate_to("Paper", "Paper 2")
        if c3.button("Paper 3"): navigate_to("Paper", "Paper 3")

# --- PAGE 2: PAPER SYLLABUS ---
def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Let's Prepare {paper}</h1>", unsafe_allow_html=True)
    
    st.write("### 📋 Updated Syllabus")
    cols = st.columns(2)
    for i, topic in enumerate(SYLLABUS[paper]):
        if cols[i%2].button(f"📌 {topic}"):
            navigate_to("Study", topic)

    st.divider()
    b1, b2, b3 = st.columns(3)
    if b1.button("📝 Give Exam"): st.toast("Exam Mode Starting...")
    if b2.button("📊 Previous Results"): st.info("No records yet.")
    if b3.button("🧠 Weak Points"): st.warning("Smart Revision Loading...")
    
    if st.button("⬅️ Back to Home"): navigate_to("Home")

# --- PAGE 3: STUDY TOPIC ---
def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    # PDF Attachment UI
    with st.expander("📂 Attached PDF Document"):
        uploaded_file = st.file_uploader("Upload PDF for this topic", type="pdf")
        if uploaded_file: st.success("PDF Context Loaded.")

    # Main Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📖 AI Notes", "💬 AI Discussion", "📝 MCQ Test", "📉 Weak Point"])
    
    with tab1:
        if st.button("✨ Generate Short Notes"):
            with st.spinner("Writing..."):
                st.write(call_ai(f"Provide smart short notes on {topic} in {st.session_state.lang}"))
    
    with tab2:
        query = st.text_input("Ask AI about this topic...")
        if query: st.write(call_ai(f"Regarding {topic}: {query}"))
        
    with tab3:
        if st.button("Generate Test"):
            st.write(call_ai(f"Generate 5 MCQs for {topic}"))
            
    with tab4:
        st.write("Tracking your progress for this topic...")

    if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

# --- NAVIGATION HELPER ---
def navigate_to(page, data=None):
    st.session_state.page = page
    if page == "Paper": st.session_state.selected_paper = data
    if page == "Study": st.session_state.selected_topic = data
    st.rerun()

# ================= APP ROUTER =================
apply_android_style()
if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Study": show_study()
    
