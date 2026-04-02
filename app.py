import streamlit as st
import random
from gtts import gTTS
import tempfile
import time

# ================== CONFIG ==================
st.set_page_config(page_title="🚀 Avyan LDCE IP Exam Masterpiece v16.0", layout="wide")

# ================== SESSION ==================
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current" not in st.session_state:
    st.session_state.current = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "weak_topics" not in st.session_state:
    st.session_state.weak_topics = []

# ================== THEME ==================
theme = st.selectbox("🎨 Theme", ["Light","Dark"])
lang = st.selectbox("🌐 Language", ["English","Hindi"])

# ================== TITLE ==================
st.title("🚀 Avyan LDCE IP Exam Masterpiece v16.0")

# ================== PAPER SELECT ==================
paper = st.selectbox("📚 Select Paper", ["Paper 1","Paper 2","Paper 3","Paper 4"])

# ================== SYLLABUS ==================
syllabus = {
    "Paper 1": ["Post Office Act 1898","IPO Rules","Savings Bank"],
    "Paper 2": ["IP Rules","Mail Manual","Parcel Rules"],
    "Paper 3": ["Hindi Grammar","Essay","Comprehension"],
    "Paper 4": ["Accounts","Statistics","Office Procedure"]
}

topic = st.selectbox("📖 Select Topic", syllabus[paper])

# ================== NOTES ==================
if st.button("📘 Load Notes"):
    st.success(f"Notes for {topic}")
    st.write(f"👉 {topic} important points (Hindi + English explanation)")

# ================== AI CHAT ==================
st.subheader("💬 AI Discussion")

user_q = st.text_input("Ask your doubt")

if user_q:
    answer = f"AI explanation for: {user_q}"
    st.write(answer)

    # 🎤 VOICE FEATURE
    voice = st.selectbox("Voice", ["Male","Female"])
    voice_lang = st.selectbox("Voice Language", ["English","Hindi"])

    if st.button("🔊 Speak"):
        tts = gTTS(text=answer, lang="hi" if voice_lang=="Hindi" else "en")
        file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(file.name)
        st.audio(file.name)

# ================== MCQ ==================
st.subheader("📝 MCQ Test")

if st.button("Generate MCQ"):
    st.session_state.questions = [
        {
            "q": f"What is {topic}?",
            "options": ["A","B","C","D"],
            "answer": "A"
        }
    ]
    st.session_state.current = 0

if st.session_state.questions:
    q = st.session_state.questions[st.session_state.current]

    st.write(q["q"])

    choice = st.radio("Choose:", q["options"])

    if st.button("Submit Answer"):
        if choice == q["answer"]:
            st.success("Correct ✅")
        else:
            st.error("Wrong ❌")
            st.session_state.weak_topics.append(topic)

# ================== FINAL EXAM ==================
st.subheader("🎯 Final Exam (Negative Marking)")

if st.button("Start Exam"):
    st.session_state.score = 0
    st.session_state.current = 0
    st.session_state.questions = [
        {"q":"Q1","options":["A","B","C","D"],"answer":"A"},
        {"q":"Q2","options":["A","B","C","D"],"answer":"B"}
    ]

if st.session_state.questions:
    q = st.session_state.questions[st.session_state.current]

    st.write(q["q"])
    ans = st.radio("Answer", q["options"], key="exam")

    if st.button("Next"):
        if ans == q["answer"]:
            st.session_state.score += 1
        else:
            st.session_state.score -= 0.25

        st.session_state.current += 1

        if st.session_state.current >= len(st.session_state.questions):
            st.success(f"Final Score: {st.session_state.score}")

# ================== WEAK TOPICS ==================
st.subheader("📉 Weak Topics")

if st.session_state.weak_topics:
    for t in set(st.session_state.weak_topics):
        st.write(f"❌ {t}")
else:
    st.success("No weak topics yet!")

# ================== SMART REVISION ==================
if st.button("🧠 Smart Revision"):
    for t in set(st.session_state.weak_topics):
        st.write(f"Revise: {t}")
