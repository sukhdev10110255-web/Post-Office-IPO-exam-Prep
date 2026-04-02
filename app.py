import streamlit as st
import os, json, re
from gtts import gTTS
import tempfile

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v17.2", layout="wide")

# ================= UI =================
st.markdown("""
<style>
.stApp {background:#f4f6fb;}
.card {
    background:white;
    padding:15px;
    border-radius:15px;
    margin:10px 0;
    box-shadow:0 3px 8px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ================= SETTINGS =================
col1,col2 = st.columns(2)
theme = col1.selectbox("🎨 Theme", ["Light","Dark"])
lang = col2.selectbox("🌐 Language", ["Bilingual","English","Hindi"])

# ================= VOICE =================
def speak(text):
    tts = gTTS(text=text, lang="hi" if lang=="Hindi" else "en")
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(file.name)
    return file.name

# ================= TITLE =================
st.title("🚀 Avyan LDCE IP Masterpiece v17.2")

# ================= SMART SEARCH =================
st.markdown("### 🌐 Smart Search")

colA, colB = st.columns([4,1])
search_query = colA.text_input("Search topic / act / rules")

search_engine = st.selectbox(
    "Choose Search Engine",
    ["Google","Bing","DuckDuckGo"]
)

if colB.button("Search"):
    if search_engine=="Google":
        st.markdown(f"https://www.google.com/search?q={search_query}")
    elif search_engine=="Bing":
        st.markdown(f"https://www.bing.com/search?q={search_query}")
    else:
        st.markdown(f"https://duckduckgo.com/?q={search_query}")

# ================= PDF =================
uploaded = st.file_uploader("📄 Upload PDF", type="pdf")

# ================= PAPER =================
paper = st.selectbox("📚 Select Paper", ["Paper 1","Paper 2","Paper 3","Paper 4"])

syllabus = {
    "Paper 1":["Post Office Act","Savings Bank Rules"],
    "Paper 2":["Mail Manual","Parcel Rules"],
    "Paper 3":["Grammar","Essay"],
    "Paper 4":["Accounts","Statistics"]
}

topic = st.text_input("🔍 Enter Topic")
if st.button("Enter Topic"):
    st.success(f"Topic selected: {topic}")

topic_select = st.selectbox("Or choose from syllabus", syllabus[paper])

final_topic = topic if topic else topic_select

# ================= NOTES =================
st.markdown('<div class="card">📘 Notes</div>', unsafe_allow_html=True)

if st.button("Generate Notes"):
    notes = f"{final_topic} notes (Hindi + English)"
    st.write(notes)

    if st.button("🔊 Voice"):
        st.audio(speak(notes))

# ================= AI CHAT =================
st.markdown('<div class="card">💬 AI Discussion</div>', unsafe_allow_html=True)

q = st.text_input("Ask doubt")
if q:
    st.write(f"Answer for {q}")

# ================= MCQ =================
st.markdown('<div class="card">📝 MCQ Test</div>', unsafe_allow_html=True)

if st.button("Generate MCQ"):
    st.session_state.mcq = [
        {"q":f"What is {final_topic}?","opt":["A","B","C","D"],"ans":"A"}
    ]

if "mcq" in st.session_state:
    for i,q in enumerate(st.session_state.mcq):
        st.write(q["q"])
        ans = st.radio("Choose", q["opt"], key=i)

        if st.button(f"Check {i}"):
            if ans == q["ans"]:
                st.success("Correct")
            else:
                st.error("Wrong")

# ================= EXAM =================
st.markdown('<div class="card">🎯 Final Exam</div>', unsafe_allow_html=True)

if st.button("Start Exam"):
    st.session_state.score = 0

    q = {"q":"Sample Q","opt":["A","B","C","D"],"ans":"A"}
    ans = st.radio(q["q"], q["opt"])

    if st.button("Submit Exam"):
        if ans == q["ans"]:
            st.session_state.score += 1
        else:
            st.session_state.score -= 0.25

        st.success(f"Score: {st.session_state.score}")

# ================= WEAK =================
st.markdown('<div class="card">📉 Weak Topics</div>', unsafe_allow_html=True)
st.write("Auto tracking coming...")

# ================= REVISION =================
if st.button("🧠 Smart Revision"):
    st.write("Revision mode started")

# ================= RANK =================
score = st.number_input("Enter score for rank prediction")
if st.button("Predict Rank"):
    st.write("Rank approx: Top 1000")
