import streamlit as st
import os
import PyPDF2
import json
import re
from datetime import datetime
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="LDCE AI Prep PRO", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
.stApp { background:#f5f7fa; }
.block { background:white; padding:15px; border-radius:12px; margin-bottom:10px; }
.chat-user { background:#d1e7ff; padding:10px; border-radius:10px; margin:5px; }
.chat-ai { background:#e2e2e2; padding:10px; border-radius:10px; margin:5px; }
</style>
""", unsafe_allow_html=True)

# ================= API =================
def get_client():
    key = os.getenv("CEREBRAS_API_KEY")
    if not key:
        st.error("API Key missing")
        st.stop()
    return Cerebras(api_key=key)

# ================= PDF =================
def extract_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for p in reader.pages:
        text += p.extract_text() or ""
    return text[:30000]  # limit safe

# ================= AI CALL =================
def ask_ai(client, prompt):
    try:
        res = client.chat.completions.create(
            model="llama3.1-8b",   # ✅ FIXED MODEL
            messages=[{"role":"user","content":prompt}],
            max_tokens=1500
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# ================= SESSION =================
if "chat" not in st.session_state:
    st.session_state.chat = []
if "weak" not in st.session_state:
    st.session_state.weak = {}

# ================= UI =================
st.title("🚀 LDCE Inspector Prep AI (V6 PRO)")

col1, col2 = st.columns(2)

topic = col1.text_area("Enter Topic")
pdf = col2.file_uploader("Upload PDF")

content = ""
if pdf:
    content = extract_pdf(pdf)
elif topic:
    content = topic

client = get_client()

# ================= BUTTONS =================
colA, colB, colC, colD = st.columns(4)

# ---------- NOTES ----------
if colA.button("📘 Notes"):
    if content:
        notes = ask_ai(client, f"Create bilingual notes (Hindi + English): {content}")
        st.markdown("### 📘 Notes")
        st.write(notes)

# ---------- MCQ ----------
if colB.button("📝 MCQ"):
    if content:
        res = ask_ai(client, f"""
        Generate 5 MCQs in JSON:
        {content}
        """)
        st.write(res)

# ---------- STUDY PLAN ----------
if colC.button("📅 Study Plan"):
    plan = ask_ai(client, "Create 7 day LDCE study plan")
    st.write(plan)

# ---------- WEAK ANALYSIS ----------
if colD.button("📊 Weak Topics"):
    st.write(st.session_state.weak)

# ================= CHAT =================
st.markdown("## 💬 AI Discussion")

user_input = st.text_input("Ask anything")

if user_input:
    st.session_state.chat.append(("user", user_input))
    reply = ask_ai(client, f"{content}\n\nUser question: {user_input}")
    st.session_state.chat.append(("ai", reply))

for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='chat-user'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-ai'>{msg}</div>", unsafe_allow_html=True)

# ================= MOCK TEST =================
st.markdown("## 🎯 Mock Test")

if st.button("Start Test"):
    questions = ask_ai(client, f"Generate 5 MCQ JSON with answers: {content}")
    st.session_state.test = questions
    st.session_state.score = 0
    st.session_state.q = 0
    st.session_state.start = datetime.now()

if "test" in st.session_state:
    st.write(st.session_state.test)

    # Timer
    elapsed = (datetime.now() - st.session_state.start).seconds
    st.write(f"⏱ Time: {elapsed}s")

    # Example scoring
    if st.button("Submit Dummy Answer"):
        st.session_state.score += 1
        st.session_state.weak["topic"] = st.session_state.weak.get("topic", 0) + 1

    st.write("Score:", st.session_state.score)
