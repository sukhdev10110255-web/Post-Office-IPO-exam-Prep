import streamlit as st
import os
from PyPDF2 import PdfReader
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG & THEME =================
st.set_page_config(page_title="Avyan LDCE 2025 Pro", layout="wide", initial_sidebar_state="collapsed")

def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-family: 'sans-serif'; font-size: 32px; padding: 10px; color: #ff4b4b; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; border: 1px solid #ccc; }}
        .syllabus-box {{ background: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #ff4b4b; color: #333; margin-bottom: 20px; }}
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

# ================= UPDATED 2025 SYLLABUS (August 2025 Order) =================
SYLLABUS_2025 = {
    "Paper 1": [
        "Post Office Act 2023", "Post Office Rules 2024", "PO Guide Part I & II", 
        "POSB Manual Vol I, II & III", "SANKALAN (PLI/RPLI Rules)", 
        "CCS Conduct Rules 1964", "CCS CCA Rules 1965", "GDS Conduct Rules 2020",
        "IT Modernization 2.0", "DIGIPIN Understanding", "PMLA Act 2002"
    ],
    "Paper 2": [
        "Noting (200 words)", "Drafting (200 words)", "Major Penalty Charge Sheet"
    ],
    "Paper 3": [
        "Constitution of India", "BNSS 2023 (Bharatiya Nagarik Suraksha Sanhita)", 
        "CAT Act 1985", "RTI Act 2005", "CCS Pension Rules 2021", 
        "GFR 2017 (Ch 2 & 6)", "FHB Vol I & II", "English Language", 
        "Reasoning & Aptitude", "Ethics in Service"
    ]
}

# ================= HYPER-SWITCH AI ENGINE =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key: return "❌ Error: CEREBRAS_API_KEY is missing in Render settings."
    
    client = Cerebras(api_key=api_key)
    
    # व्यापक मॉडल लिस्ट ताकि 404 एरर न आए
    models_to_test = [
        "llama-3.3-70b-versatile", 
        "llama3.3-70b", 
        "llama-3.1-70b-versatile",
        "llama-3.1-8b"
    ]
    
    for model in models_to_test:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[{"role":"system", "content": f"Expert LDCE Tutor. Language: {st.session_state.lang}"},
                          {"role":"user", "content": prompt}],
                max_tokens=1500
            )
            st.session_state.active_model = model
            return res.choices[0].message.content
        except:
            continue # अगले मॉडल पर जाएँ
            
    return "⚠️ AI connectivity failed. Cerebras might be down or API key expired."

# ================= APP PAGES =================

def show_home():
    col_l, col_r = st.columns([3, 1])
    with col_r:
        st.session_state.theme = st.selectbox("🎨 Theme", ["Light", "Dark"])
        st.session_state.lang = st.selectbox("🌐 Language", ["Bilingual", "Hindi", "English"])
    
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    
    m_l, m_c, m_r = st.columns([1, 2, 1])
    with m_c:
        search_q = st.text_input("🔍 Smart Search", placeholder="Topic name...")
        if st.button("Search Online"):
            st.write(f"https://www.google.com/search?q={search_q}+India+Post+LDCE")
        
        st.divider()
        st.subheader("Choose Your Exam Paper (New Pattern)")
        p1, p2, p3 = st.columns(3)
        if p1.button("Paper 1"): navigate_to("Paper", "Paper 1")
        if p2.button("Paper 2"): navigate_to("Paper", "Paper 2")
        if p3.button("Paper 3"): navigate_to("Paper", "Paper 3")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Let's Prepare {paper}</h1>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='syllabus-box'><b>{paper} Syllabus (Aug 2025):</b> Select a topic to generate notes.</div>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, topic in enumerate(SYLLABUS_2025[paper]):
        if cols[i%2].button(f"📘 {topic}"):
            navigate_to("Study", topic)
    
    st.divider()
    if st.button("⬅️ Back to Home"): navigate_to("Home")

def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 AI Notes", "💬 AI Chat", "📝 MCQ Quiz", "📊 Progress"])
    
    with tab1:
        if st.button("✨ Generate Pro Notes"):
            with st.spinner("Connecting to Secure AI..."):
                st.markdown(call_ai(f"Provide detailed notes on '{topic}' for IP Exam (2025 Syllabus)."))
    
    with tab2:
        q = st.chat_input("Ask about this rule...")
        if q: st.write(call_ai(f"Question about {topic}: {q}"))
        
    with tab3:
        if st.button("Generate Test"):
            st.markdown(call_ai(f"Generate 5 MCQs on {topic} with answers."))
            
    with tab4:
        st.info("Performance stats will appear here.")

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

st.sidebar.caption(f"Status: V22.1 Stable | Active Model: {st.session_state.active_model}")
