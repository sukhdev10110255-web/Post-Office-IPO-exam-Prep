import streamlit as st
import os
import time
from cerebras.cloud.sdk import Cerebras

# ================= 1. CONFIG =================
st.set_page_config(page_title="Avyan LDCE Premium", layout="wide", initial_sidebar_state="collapsed")

def apply_android_style():
    theme_bg = "#121212" if st.session_state.get('theme', 'Light') == "Dark" else "#F0F2F6"
    text_col = "white" if st.session_state.get('theme', 'Light') == "Dark" else "black"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_col}; }}
        .header-text {{ text-align: center; font-weight: bold; font-size: 30px; color: #ff4b4b; padding: 10px; }}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; border: 1px solid #ccc; }}
        .premium-lock {{ background: #fff3e0; border: 2px dashed #ff9800; padding: 20px; border-radius: 15px; text-align: center; color: #e65100; }}
        </style>
    """, unsafe_allow_html=True)

# ================= 2. STATE MANAGEMENT =================
if "page" not in st.session_state:
    st.session_state.update({
        "page": "Home",
        "theme": "Light",
        "lang": "Bilingual",
        "is_premium": False, # DEFAULT: USER IS NOT PREMIUM
        "selected_paper": None,
        "selected_topic": None,
        "exam_history": []
    })

# ================= 3. SYLLABUS DATA (Aug 2025) =================
SYLLABUS_2025 = {
    "Paper 1": ["Post Office Act 2023", "Post Office Rules 2024", "PO Guide I & II", "POSB Manual", "IT Modernization 2.0"],
    "Paper 2": ["Noting (15 Marks)", "Drafting (15 Marks)", "Major Penalty Charge Sheet (Rule 14)"],
    "Paper 3": ["Constitution of India", "BNSS 2023", "CAT Act 1985", "RTI Act 2005", "Ethics & Reasoning"]
}

# ================= 4. PREMIUM GATEKEEPER =================
def check_premium_access():
    if not st.session_state.is_premium:
        st.markdown("""
            <div class='premium-lock'>
                <h3>🔒 Premium Feature Locked</h3>
                <p>इस टेस्ट और एग्जाम को अनलॉक करने के लिए प्रीमियम सब्सक्रिप्शन लें।</p>
                <p><b>Price: ₹999 / Year</b></p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("💳 Pay & Unlock Now"):
            st.session_state.is_premium = True
            st.success("Congratulations! You are now a Premium Member.")
            st.rerun()
        return False
    return True

# ================= 5. PAGES =================

def show_home():
    st.markdown("<h1 class='header-text'>Welcome Trainee</h1>", unsafe_allow_html=True)
    if st.session_state.is_premium:
        st.sidebar.success("⭐ Premium Active")
    else:
        st.sidebar.warning("🆓 Free Version")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Paper 1"): navigate_to("Paper", "Paper 1")
    if c2.button("Paper 2"): navigate_to("Paper", "Paper 2")
    if c3.button("Paper 3"): navigate_to("Paper", "Paper 3")

def show_paper():
    paper = st.session_state.selected_paper
    st.markdown(f"<h1 class='header-text'>{paper}</h1>", unsafe_allow_html=True)
    for topic in SYLLABUS_2025.get(paper, []):
        if st.button(f"📌 {topic}"): navigate_to("Study", topic)
    
    st.divider()
    if st.button("📝 Take Live Exam (Premium)"):
        navigate_to("Exam")

def show_study():
    topic = st.session_state.selected_topic
    st.markdown(f"<h1 class='header-text'>{topic}</h1>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["📖 Free Notes", "📝 Premium MCQ Test"])
    with t1:
        st.write("Free summary notes are available here.")
        if st.button("Generate Detailed AI Notes"):
            st.write("Notes generated...")
            
    with t2:
        if check_premium_access():
            st.write("Generating Premium MCQs for you...")
            # MCQ Logic here

    if st.button("⬅️ Back"): navigate_to("Paper", st.session_state.selected_paper)

def show_exam():
    st.markdown("<h1 class='header-text'>Official Mock Exam</h1>", unsafe_allow_html=True)
    if check_premium_access():
        st.success("Access Granted! Loading 2024 Question Paper...")
        # [span_0](start_span)Official 2024 Exam Logic here[span_0](end_span)

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
    
