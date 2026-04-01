import streamlit as st
import os
import PyPDF2
import json
import re
from datetime import datetime
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="LDCE Prep AI PRO", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
.stApp { background:#f5f7fa; }
.block { background:white; padding:15px; border-radius:12px; margin-bottom:10px; }
.question-card { background:white; padding:15px; border-left:4px solid #1e3c72; border-radius:10px; margin-bottom:10px; }
.chat-user { background:#d1e7ff; padding:10px; border-radius:10px; margin:5px; }
.chat-ai { background:#e2e2e2; padding:10px; border-radius:10px; margin:5px; }
</style>
""", unsafe_allow_html=True)

# ================= API =================
def get_client():
    key = os.getenv("CEREBRAS_API_KEY")
    if not key:
        st.error("❌ Add CEREBRAS_API_KEY in Render")
        st.stop()
    return Cerebras(api_key=key)

# ================= PDF =================
def extract_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for p in reader.pages:
        text += p.extract_text() or ""
    return text[:20000]

# ================= AI =================
def ask_ai(client, prompt):
    try:
        res = client.chat.completions.create(
            model="llama3.1-8b",
            messages=[{"role":"user","content":prompt}],
            max_tokens=1500
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# ================= JSON FIX =================
def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None
    return None

# ================= SESSION =================
if "chat" not in st.session_state:
    st.session_state.chat = []
if "questions" not in st.session_state:
    st.session_state.questions = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "weak" not in st.session_state:
    st.session_state.weak = {}

# ================= UI =================
st.title("🚀 LDCE Inspector Prep AI (PRO)")

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

# NOTES
if colA.button("📘 Notes"):
    if content:
        notes = ask_ai(client, f"Create structured bilingual notes (Hindi + English): {content}")
        st.markdown("### 📘 Notes")
        st.write(notes)

# MCQ GENERATE
if colB.button("📝 Generate MCQ"):
    if content:
        res = ask_ai(client, f"""
        Generate 5 MCQs in JSON:
        {content}
        """)
        data = extract_json(res)
        if data:
            st.session_state.questions = data.get("questions", [])
        else:
            st.error("MCQ parsing error")

# STUDY PLAN
if colC.button("📅 Study Plan"):
    plan = ask_ai(client, "Create 7 day study plan for LDCE exam")
    st.write(plan)

# WEAK TOPICS
if colD.button("📊 Weak Topics"):
    st.write(st.session_state.weak)

# ================= MCQ PRACTICE =================
st.markdown("## 📝 MCQ Practice")

for i, q in enumerate(st.session_state.questions):

    st.markdown(f"<div class='question-card'><b>Q{i+1}:</b> {q['question']}</div>", unsafe_allow_html=True)

    selected = st.radio("Choose answer:", q["options"], key=f"q_{i}")

    if st.button(f"Check Answer {i+1}", key=f"btn_{i}"):

        if selected == q["correct_answer"]:
            st.success("✅ Correct")
            st.session_state.score += 1
        else:
            st.error("❌ Wrong")
            st.session_state.weak[q["question"]] = st.session_state.weak.get(q["question"], 0) + 1

        with st.expander("Explanation"):
            st.write("Correct:", q["correct_answer"])
            st.write(q["explanation"])

    st.markdown("---")

# ================= CHAT =================
st.markdown("## 💬 AI Chat")

user_input = st.text_input("Ask anything about topic")

if user_input:
    st.session_state.chat.append(("user", user_input))
    reply = ask_ai(client, f"{content}\nUser question: {user_input}")
    st.session_state.chat.append(("ai", reply))

for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='chat-user'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-ai'>{msg}</div>", unsafe_allow_html=True)

# ================= MOCK TEST =================
st.markdown("## 🎯 Mock Test")

if st.button("Start Test"):
    st.session_state.score = 0
    st.session_state.start = datetime.now()

if "start" in st.session_state:
    elapsed = (datetime.now() - st.session_state.start).seconds
    st.write(f"⏱ Time: {elapsed}s")
    st.write(f"🎯 Score: {st.session_state.score}")
