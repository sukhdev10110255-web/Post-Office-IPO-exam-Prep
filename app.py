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
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; border: 1px solid #ccc; background-color: white; color: black; }}
        .stButton>button:hover {{ border-color: #ff4b4b; color: #ff4b4b; }}
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
        "selected_topic": None
    })

# ================= UPDATED SYLLABUS (As per 22.08.2025 Order) =================
# [span_4](start_span)[span_5](start_span)[span_6](start_span)[span_7](start_span)Based on[span_4](end_span)[span_5](end_span)[span_6](end_span)[span_7](end_span)
SYLLABUS_2025 = {
    "Paper 1": [
        "Post Office Act 2023", "Post Office Rules 2024", "PO Guide Part I & II", 
        "POSB Manual Vol I, II & III", "SANKALAN (PLI/RPLI Rules 2011)", 
        "CCS Conduct Rules 1964", "CCS CCA Rules 1965", "GDS Conduct Rules 2020",
        "IT Modernization 2.0 (APT Knowledge)", "DIGIPIN Basic Understanding",
        "PMLA Act 2002", "Consumer Protection Act 2019"
    ],
    "Paper 2": [
        "Noting (Approx 200 words)", 
        "Drafting (Approx 200 words)", 
        "Draft Major Penalty Charge Sheet"
    ],
    "Paper 3": [
        "Constitution of India (Fundamental Rights/Duties)", 
        "Bharatiya Nagarik Suraksha Sanhita 2023 (BNSS)", 
        "Central Administrative Tribunal Act 1985", 
        "RTI Act 2005 & Rules 2012", "CCS Pension Rules 2021", 
        "General Financial Rules 2017 (Ch 2 & 6)", "P&T FHB Vol I & Postal FHB Vol II",
        "English Language Questions", "Reasoning & Quantitative Aptitude",
        "Ethics & Interpersonal Skills"
    ]
}

# ================= AI ENGINE =================
def call_ai(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY")
    client = Cerebras(api_key=api_key)
    try:
        # Using Llama 3.3 for high accuracy in departmental rules
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system", "content": f"You are an expert LDCE tutor. Language: {st.session_state.lang}"},
                      {"role":"user", "content": prompt}],
            max_tokens=2000
        )
        return res.choices[0].message.content
    except:
        return "⚠️ AI Error. Please check your API Key or Network."

# ================= PAGE ROUTING =================

def show_home():
    col_empty, col_ctrl = st.columns([3, 1])
    with col_ctrl:
        st.session_state.theme = st.selectbox("🎨 Theme", ["Light", "Dark"])
        st.session_state.lang = st.selectbox("🌐 Language", ["Bilingual", "Hindi", "English"])
    
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    
    mid_l, mid_c, mid_r = st.columns([1, 2, 1])
    with mid_c:
        # Search Section
        search_q = st.text_input("🔍 Smart Topic Search", placeholder="Type rule or section...")
        s1, s2, s3 = st.columns(3)
        if s1.button("Google"): st.write(f"https://www.google.com/search?q={search_q}+India+Post")
        if s2.button("Bing"): st.write(f"https://www.bing.com/search?q={search_q}")
        if s3.button("Rules"): st.write(f"https://www.indiapost.gov.in/")
        
        st.divider()
        st.subheader("Choose Your Exam Paper (New Pattern)")
        p1, p2, p3 = st.columns(3)
        if p1.button("Paper 1 (250m)"): navigate_to("Paper", "Paper 1")
        if p2.button("Paper 2 (50m)"): navigate_to("Paper", "Paper 2")
        if p3.button("Paper 3 (300m)"): navigate_to("Paper", "Paper 3")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>Let's Prepare {paper}</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"<div class='syllabus-box'><b>Current Syllabus for {paper}:</b> Click any topic below to start learning.</div>", unsafe_allow_html=True)
        cols = st.columns(2)
        for i, topic in enumerate(SYLLABUS_2025[paper]):
            if cols[i%2].button(f"📘 {topic}"):
                navigate_to("Study", topic)

    st.divider()
    b1, b2, b3 = st.columns(3)
    if b1.button("📝 Give Exam"): st.warning("Exam Mode starting...")
    if b2.button("📊 Results"): st.info("Previous results will appear here.")
    if b3.button("🧠 Weak Points"): st.error("Focusing on weak areas...")
    
    if st.button("⬅️ Back to Home"): navigate_to("Home")

def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    # PDF UI
    with st.expander("📂 Topic Reference PDF"):
        st.file_uploader("Attach PDF for this topic", type="pdf")

    # Study Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📖 AI Notes", "💬 AI Chat", "📝 MCQ Quiz", "📈 Progress"])
    
    with tab1:
        if st.button("✨ Generate Pro Notes"):
            with st.spinner("AI analyzing latest 2025 guidelines..."):
                st.markdown(call_ai(f"Provide professional notes on '{topic}' based on the Post Office Act 2023 and updated 2025 syllabus."))
    
    with tab2:
        q = st.chat_input("Ask a doubt about this rule...")
        if q: st.write(call_ai(f"Regarding {topic}: {q}"))
        
    with tab3:
        if st.button("Start MCQ Test"):
            st.markdown(call_ai(f"Generate 5 MCQs on {topic} for LDCE IP Exam."))
            
    with tab4:
        st.write("Performance analysis coming soon.")

    if st.button("⬅️ Back to Syllabus"): navigate_to("Paper", st.session_state.selected_paper)

def navigate_to(page, data=None):
    st.session_state.page = page
    if data:
        if page == "Paper": st.session_state.selected_paper = data
        if page == "Study": st.session_state.selected_topic = data
    st.rerun()

# ================= MAIN =================
apply_android_style()
if st.session_state.page == "Home": show_home()
elif st.session_state.page == "Paper": show_paper()
elif st.session_state.page == "Study": show_study()
    
