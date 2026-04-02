import streamlit as st
import os, json, re, random
from gtts import gTTS
import tempfile
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v17", layout="wide")

# ================= SETTINGS =================
col1, col2 = st.columns([1,1])
with col1:
    theme = st.selectbox("🎨 Theme", ["Light","Dark"])
with col2:
    lang = st.selectbox("🌐 Language", ["Bilingual","English","Hindi"])

if theme=="Dark":
    st.markdown("<style>.stApp{background:#0e1117;color:white}</style>", unsafe_allow_html=True)

def format_prompt(text):
    if lang=="English": return f"Answer in English:\n{text}"
    elif lang=="Hindi": return f"Answer in Hindi:\n{text}"
    else: return f"Answer in Hindi and English:\n{text}"

# ================= AI =================
def ai(prompt):
    try:
        client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
        res = client.chat.completions.create(
            model="llama3.1-8b-instant",
            messages=[{"role":"user","content":prompt}],
            max_tokens=1200
        )
        return res.choices[0].message.content
    except:
        return "AI Error"

# ================= VOICE =================
def speak(text):
    tts = gTTS(text=text, lang="hi" if lang=="Hindi" else "en")
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(file.name)
    return file.name

# ================= SESSION =================
defaults = {
    "page":"home",
    "paper":"",
    "topic":"",
    "questions":[],
    "weak":{},
    "score":0,
    "exam_index":0,
    "exam_q":[]
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ================= BASE SYLLABUS =================
base_syllabus = {
    "Paper 1":[
        "Indian Post Office Act 1898",
        "Post Office Guide Part I",
        "Savings Bank Rules",
        "Postal Manual Volume VI"
    ],
    "Paper 2":[
        "Mail Manual",
        "Parcel Rules",
        "IP Rules"
    ],
    "Paper 3":[
        "Hindi Grammar",
        "Essay Writing",
        "Comprehension"
    ],
    "Paper 4":[
        "Accounts",
        "Statistics",
        "Office Procedure"
    ]
}

# ================= HOME =================
if st.session_state.page=="home":

    st.title("🚀 Avyan LDCE IP Masterpiece v17.0")

    col1,col2,col3,col4 = st.columns(4)

    if col1.button("📘 Paper 1"):
        st.session_state.paper="Paper 1"; st.session_state.page="syllabus"
    if col2.button("📗 Paper 2"):
        st.session_state.paper="Paper 2"; st.session_state.page="syllabus"
    if col3.button("📙 Paper 3"):
        st.session_state.paper="Paper 3"; st.session_state.page="syllabus"
    if col4.button("📕 Paper 4"):
        st.session_state.paper="Paper 4"; st.session_state.page="syllabus"

# ================= SYLLABUS =================
elif st.session_state.page=="syllabus":

    st.title(f"{st.session_state.paper} Syllabus")

    if st.button("⬅️ Back"):
        st.session_state.page="home"

    # base syllabus
    topics = base_syllabus.get(st.session_state.paper, [])

    st.subheader("📚 Topics")
    for t in topics:
        if st.button(t):
            st.session_state.topic = t
            st.session_state.page="topic"

    # AI expand
    if st.button("🤖 Load Full AI Syllabus"):
        ai_topics = ai(f"Give full syllabus topics list for {st.session_state.paper}")
        st.write(ai_topics)

# ================= TOPIC =================
elif st.session_state.page=="topic":

    st.title(f"📖 {st.session_state.topic}")

    if st.button("⬅️ Back"):
        st.session_state.page="syllabus"

    # ---------- NOTES ----------
    st.subheader("📖 Notes")
    notes = ai(format_prompt(f"Short exam notes:\n{st.session_state.topic}"))
    st.write(notes)

    # ---------- VOICE ----------
    if st.button("🔊 Listen Notes"):
        audio = speak(notes)
        st.audio(audio)

    # ---------- CHAT ----------
    st.subheader("💬 AI Discussion")
    q = st.text_input("Ask doubt")
    if q:
        ans = ai(q)
        st.write(ans)

        if st.button("🔊 Speak Answer"):
            st.audio(speak(ans))

    # ---------- MCQ ----------
    st.subheader("📝 MCQ Test")

    if st.button("Generate MCQ"):
        res = ai(f"Generate 5 MCQs JSON:\n{st.session_state.topic}")
        try:
            data = json.loads(re.search(r'\{.*\}', res, re.DOTALL).group())
            st.session_state.questions = data["questions"]
        except:
            st.error("MCQ error")

    for i,q in enumerate(st.session_state.questions):
        st.write(q["question"])
        ans = st.radio("Choose", q["options"], key=f"q{i}")

        if st.button(f"Check {i}"):
            if ans == q["correct_answer"]:
                st.success("Correct")
            else:
                st.error("Wrong")
                st.session_state.weak[q["question"]] = q["correct_answer"]

    # ---------- EXAM ----------
    st.subheader("🎯 Final Exam")

    if st.button("Start Exam"):
        st.session_state.exam_q = st.session_state.questions
        st.session_state.exam_index = 0
        st.session_state.score = 0

    if st.session_state.exam_q:
        q = st.session_state.exam_q[st.session_state.exam_index]
        st.write(q["question"])
        ans = st.radio("Answer", q["options"], key="exam")

        if st.button("Next"):
            if ans == q["correct_answer"]:
                st.session_state.score += 1
            else:
                st.session_state.score -= 0.25

            st.session_state.exam_index += 1

            if st.session_state.exam_index >= len(st.session_state.exam_q):
                st.success(f"Final Score: {st.session_state.score}")

    # ---------- WEAK ----------
    st.subheader("📉 Weak Topics")
    st.write(st.session_state.weak)

    if st.button("🧠 Smart Revision"):
        st.write(ai(format_prompt(f"Teach weak topics:\n{list(st.session_state.weak.keys())}")))
