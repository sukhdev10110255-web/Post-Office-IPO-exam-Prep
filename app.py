import streamlit as st
import random

st.set_page_config(layout="wide")

# ================= UI =================
st.markdown("""
<style>
.stApp {background:#eef2f7;}
.box {
    background:white;
    padding:15px;
    border-radius:15px;
    margin:10px 0;
    box-shadow:0 2px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "weak" not in st.session_state:
    st.session_state.weak = []

if "mcq" not in st.session_state:
    st.session_state.mcq = []

# ================= TITLE =================
st.title("🚀 Avyan LDCE v17.3 PRO")

# ================= PAPER =================
paper = st.selectbox("📚 Select Paper", ["Paper 1","Paper 2","Paper 3","Paper 4"])

syllabus = {
    "Paper 1":["Savings Bank Rules","Post Office Act"],
    "Paper 2":["Mail Manual","Parcel Rules"],
    "Paper 3":["Grammar","Essay"],
    "Paper 4":["Accounts","Statistics"]
}

# ================= TOPIC =================
topic_input = st.text_input("🔍 Enter Topic")

if st.button("Enter Topic"):
    st.session_state.topic = topic_input

topic_select = st.selectbox("Or choose topic", syllabus[paper])

final_topic = st.session_state.get("topic") or topic_select

# ================= NOTES =================
st.markdown('<div class="box">📘 Notes</div>', unsafe_allow_html=True)

if st.button("Generate Notes"):
    notes = f"""
    🔹 {final_topic}

    👉 English:
    {final_topic} is important for LDCE exam.

    👉 हिंदी:
    {final_topic} परीक्षा के लिए महत्वपूर्ण है।
    """
    st.write(notes)

# ================= MCQ =================
st.markdown('<div class="box">📝 MCQ Test</div>', unsafe_allow_html=True)

if st.button("Generate MCQ"):

    st.session_state.mcq = [
        {
            "q":f"What is {final_topic}?",
            "options":["Rule","Act","Scheme","None"],
            "ans":"Rule"
        },
        {
            "q":f"{final_topic} belongs to?",
            "options":["Banking","Postal","Railway","Law"],
            "ans":"Postal"
        }
    ]

# MCQ UI
for i,q in enumerate(st.session_state.mcq):
    st.write(f"Q{i+1}: {q['q']}")

    choice = st.radio("Choose", q["options"], key=i)

    if st.button(f"Check {i}"):

        if choice == q["ans"]:
            st.success("✅ Correct")
        else:
            st.error("❌ Wrong")

            # 🔥 WEAK TRACKING
            if final_topic not in st.session_state.weak:
                st.session_state.weak.append(final_topic)

# ================= EXAM =================
st.markdown('<div class="box">🎯 Final Exam</div>', unsafe_allow_html=True)

if st.button("Start Exam"):

    score = 0

    for q in st.session_state.mcq:
        ans = st.radio(q["q"], q["options"])

        if ans == q["ans"]:
            score += 1
        else:
            score -= 0.25

    st.success(f"Final Score: {score}")

# ================= WEAK =================
st.markdown('<div class="box">📉 Weak Topics</div>', unsafe_allow_html=True)

if st.session_state.weak:
    for t in st.session_state.weak:
        st.write(f"❌ {t}")
else:
    st.success("No weak topics yet")

# ================= REVISION =================
if st.button("🧠 Smart Revision"):
    for t in st.session_state.weak:
        st.write(f"Revise: {t}")
