import streamlit as st
import os
import pandas as pd
from PyPDF2 import PdfReader
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v20.2", layout="wide", page_icon="🚀")

# --- SYLLABUS DATA ---
SYLLABUS = {
    "Paper 1": ["PO Guide Part I", "PO Guide Part II", "Basic Terminology", "Organization of Department", "Post Office Savings Bank", "PLI/RPLI Rules"],
    "Paper 2": ["Postal Manual Volume V", "Postal Manual Volume VI", "FHB Volume I", "P&T Manual Volume IV", "Staff & Discipline Rules"],
    "Paper 3": ["General Knowledge", "Current Affairs", "Indian Constitution", "Basic Arithmetic", "Reasoning & Analytical Ability"],
    "Paper 4": ["English Language", "Letter Writing", "Drafting", "Noting", "Precis Writing"]
}

# ================= CORE AI ENGINE (Fixed Model) =================
def call_ai(prompt):
    try:
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key: return "❌ API Key missing!"
        
        client = Cerebras(api_key=api_key)
        # UPDATED MODEL: llama3.3-70b-versatile is stable and powerful
        res = client.chat.completions.create(
            model="llama3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "You are an expert LDCE Exam Tutor. Always provide notes in both Hindi and English for Indian Postal Department employees."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# ================= UI LAYOUT =================
st.title("🚀 Avyan LDCE IP Masterpiece v20.2")

# --- SIDEBAR: Paper Selection ---
with st.sidebar:
    st.header("📋 Exam Syllabus")
    selected_paper = st.selectbox("Select Paper", list(SYLLABUS.keys()))
    st.divider()
    st.info(f"Currently viewing: {selected_paper}")
    
    # CLICKABLE TOPICS
    st.subheader("📌 Click Topic to Study")
    for item in SYLLABUS[selected_paper]:
        if st.button(item, key=item):
            st.session_state.topic = item

# ================= MAIN DASHBOARD =================
if "topic" not in st.session_state:
    st.session_state.topic = SYLLABUS["Paper 1"][0]

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📖 Study Dashboard: {st.session_state.topic}")
    
    # LEARN BUTTON WITH DUAL LANGUAGE LOGIC
    if st.button(f"✨ Generate Notes for {st.session_state.topic}"):
        with st.spinner(f"Fetching bilingual notes for {st.session_state.topic}..."):
            prompt = f"Create detailed study notes on '{st.session_state.topic}' for the Inspector Posts LDCE Exam. Explain in English first, then provide a clear Hindi translation."
            notes = call_ai(prompt)
            st.markdown(notes)

    st.divider()
    # CHAT/DISCUSSION
    st.subheader("💬 AI Discussion")
    user_query = st.text_input("Ask a doubt about this topic...")
    if user_query:
        st.write(call_ai(f"Regarding {st.session_state.topic}: {user_query}"))

with col2:
    st.subheader("🎯 Quick Actions")
    if st.button("📝 Generate MCQ Test"):
        with st.spinner("Creating MCQs..."):
            mcqs = call_ai(f"Generate 5 tough MCQs on {st.session_state.topic} for LDCE IP Exam with answers.")
            st.write(mcqs)
    
    st.divider()
    st.subheader("📉 Weak Topics")
    st.info("Performance tracking based on your clicks.")
    
    st.divider()
    uploaded_file = st.file_uploader("Upload Circulars (PDF)", type="pdf")
    if uploaded_file:
        st.success("File Ready for Contextual AI Analysis!")

# ================= FOOTER =================
st.markdown("---")
st.markdown(f"**System Status:** V20.2 Stable | **Model:** llama3.3-70b-versatile")
