import streamlit as st
import os
import pandas as pd
from PyPDF2 import PdfReader
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v20.3", layout="wide", page_icon="🚀")

# --- FULL SYLLABUS DATA (Paper 1 to 4) ---
SYLLABUS = {
    "Paper 1": [
        "PO Guide Part I (General)", "PO Guide Part II (Foreign Post)", 
        "POSB Manual Vol I & II", "PLI/RPLI Rules 2024", 
        "IT Modernization Project 2.0", "Post Office Act 2023"
    ],
    "Paper 2": [
        "Postal Manual Volume V", "Postal Manual Volume VI (Part I, II, III)", 
        "Postal Manual Volume VII", "FHB Volume I & II", 
        "CCS Conduct Rules 1964", "CCS CCA Rules 1965"
    ],
    "Paper 3": [
        "Indian Constitution", "Indian Economy & Post", 
        "General Awareness", "Logical Reasoning", 
        "Basic Mathematics (Percentage, Profit/Loss, Interest)"
    ],
    "Paper 4": [
        "English to Hindi Translation", "Hindi to English Translation", 
        "Letter Writing (Official)", "Drafting & Noting", "Precis Writing"
    ]
}

# ================= AI ENGINE (Auto-Switching Logic) =================
def call_ai(prompt):
    # Try these models in order until one works
    models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama3.1-8b"]
    
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key: return "❌ Error: API Key missing in Render Environment."

    client = Cerebras(api_key=api_key)
    
    for model_name in models_to_try:
        try:
            res = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an expert LDCE Exam Tutor for India Post. Provide notes in Hindi and English."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            return res.choices[0].message.content, model_name
        except Exception:
            continue # Try next model if this one fails
            
    return "⚠️ All models failed. Please check Cerebras Dashboard for latest model names.", "None"

# ================= UI LAYOUT =================
st.title("🚀 Avyan LDCE IP Masterpiece v20.3")

# --- SIDEBAR: Paper & Clickable Topics ---
with st.sidebar:
    st.header("📋 Exam Selection")
    paper_choice = st.selectbox("Choose Paper", list(SYLLABUS.keys()))
    st.divider()
    
    st.subheader("📌 Topics (Click to Load)")
    for topic in SYLLABUS[paper_choice]:
        if st.button(topic):
            st.session_state.current_topic = topic

# ================= MAIN DASHBOARD =================
if "current_topic" not in st.session_state:
    st.session_state.current_topic = SYLLABUS["Paper 1"][0]

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader(f"📖 Subject: {st.session_state.current_topic}")
    
    if st.button(f"✨ Generate Pro Notes (Hindi + English)"):
        with st.spinner("AI is analyzing departmental rules..."):
            notes_prompt = f"Explain '{st.session_state.current_topic}' in detail for Inspector Posts Exam. Use bullet points. Provide English content first, followed by a Hindi translation."
            content, used_model = call_ai(notes_prompt)
            st.session_state.latest_notes = content
            st.session_state.active_model = used_model
            st.markdown(content)

    st.divider()
    st.subheader("💬 AI Discussion")
    query = st.chat_input("Ask a doubt...")
    if query:
        st.write(f"**You:** {query}")
        ans, _ = call_ai(f"Topic: {st.session_state.current_topic}. Question: {query}")
        st.write(f"**AI:** {ans}")

with col_right:
    st.subheader("🎯 Quick Tools")
    if st.button("📝 Create MCQ Practice"):
        with st.spinner("Generating 5 MCQs..."):
            q_prompt = f"Generate 5 tough MCQs on {st.session_state.current_topic} with options and hidden answers."
            mcqs, _ = call_ai(q_prompt)
            st.write(mcqs)
    
    st.divider()
    st.subheader("📂 Reference PDF")
    pdf = st.file_uploader("Upload Circular", type="pdf")
    if pdf:
        st.success("PDF Context Active!")

# --- FOOTER ---
st.markdown("---")
active_m = st.session_state.get('active_model', 'Searching...')
st.caption(f"System: V20.3 Stable | Active Model: {active_m} | User: Satya Prakash Yadav")
