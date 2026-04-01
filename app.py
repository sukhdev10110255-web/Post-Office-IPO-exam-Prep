import streamlit as st
import os, json, re
import PyPDF2
from datetime import datetime
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE IP Exam Masterpiece v13.0", layout="wide")

# ================= SETTINGS =================
theme = st.selectbox("🎨 Theme", ["Light","Dark"])
lang = st.selectbox("🌐 Language", ["Bilingual","English","Hindi"])

if theme == "Dark":
    st.markdown("<style>.stApp{background:#0e1117;color:white}</style>", unsafe_allow_html=True)

def format_prompt(text):
    if lang=="English": return f"Answer in English:\n{text}"
    elif lang=="Hindi": return f"Answer in Hindi:\n{text}"
    else:
        return f"""
        Answer in BOTH English and Hindi.

        English:
        ---
        Hindi:
        ---
        Content:
        {text}
        """

# ================= AI =================
def ai(prompt):
    client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
    res = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[{"role":"user","content":prompt}],
        max_tokens=1500
    )
    return res.choices[0].message.content

# ================= PDF =================
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() or "" for p in reader.pages])[:20000]

# ================= SESSION =================
for key in ["page","chat","questions","weak","score","exam_q","index"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["chat","questions","exam_q"] else 0 if key=="score" else {} if key=="weak" else "home" if key=="page" else 0

# ================= HOME =================
if st.session_state.page=="home":
    st.title("🚀 Avyan LDCE IP Exam Masterpiece v13.0")
    st.subheader("Select Paper")

    cols = st.columns(4)
    for i,p in enumerate(["Paper 1","Paper 2","Paper 3","Paper 4"]):
        if cols[i].button(p):
            st.session_state.paper=p
            st.session_state.page="mode"

# ================= MODE =================
elif st.session_state.page=="mode":
    st.title(f"{st.session_state.paper}")

    c1,c2,c3 = st.columns(3)
    if c1.button("🔍 Topic"): st.session_state.input="topic"; st.session_state.page="study"
    if c2.button("📄 PDF"): st.session_state.input="pdf"; st.session_state.page="study"
    if c3.button("🤖 AI Course"): st.session_state.input="ai"; st.session_state.page="study"

# ================= STUDY =================
elif st.session_state.page=="study":

    st.title("📚 Study Dashboard")

    content = ""

    if st.session_state.input=="topic":
        content = st.text_area("Enter Topic")

    elif st.session_state.input=="pdf":
        pdf = st.file_uploader("Upload PDF")
        if pdf: content = read_pdf(pdf)

    elif st.session_state.input=="ai":
        content = ai(format_prompt(f"Generate syllabus with Acts, Rules, Topics for {st.session_state.paper}"))

    # ========= MODES =========
    st.markdown("## 🎯 Choose Mode")

    col1,col2,col3,col4,col5 = st.columns(5)

    # LEARNING
    if col1.button("📖 Learn"):
        st.write(ai(format_prompt(f"Explain in structured notes: {content}")))

    # CHAT
    if col2.button("💬 Chat"):
        q = st.text_input("Ask")
        if q:
            st.session_state.chat.append(("user",q))
            reply = ai(format_prompt(f"{content}\nUser:{q}"))
            st.session_state.chat.append(("ai",reply))

    for role,msg in st.session_state.chat:
        st.write(f"**{role}:** {msg}")

    # MCQ
    if col3.button("📝 MCQ"):
        res = ai(format_prompt(f"Generate MCQs JSON: {content}"))
        try:
            st.session_state.questions = json.loads(re.search(r'\{.*\}', res, re.DOTALL).group())["questions"]
        except:
            st.error("MCQ error")

    # MCQ UI
    for i,q in enumerate(st.session_state.questions):
        st.write(q["question"])
        ans = st.radio("Choose", q["options"], key=i)

        if st.button(f"Check {i}"):
            if ans==q["correct_answer"]:
                st.success("Correct")
            else:
                st.error("Wrong")
                st.session_state.weak[q["question"]] = 1

    # MOCK
    if col4.button("🎯 Mock"):
        st.write(ai(format_prompt(f"Generate mock test: {content}")))

    # FINAL EXAM
    if col5.button("🧪 Final Exam"):
        data = ai("Generate 10 MCQ JSON exam")
        try:
            st.session_state.exam_q = json.loads(re.search(r'\{.*\}', data, re.DOTALL).group())["questions"]
            st.session_state.index=0
            st.session_state.score=0
            st.session_state.start=datetime.now()
        except:
            st.error("Exam error")

    # ===== EXAM ENGINE =====
    if st.session_state.exam_q:
        st.subheader("Exam Running")

        time = (datetime.now()-st.session_state.start).seconds
        st.write(f"⏱ {time}s")

        q = st.session_state.exam_q[st.session_state.index]
        st.write(q["question"])
        ans = st.radio("Answer", q["options"], key="exam")

        if st.button("Submit"):
            if ans==q["correct_answer"]:
                st.session_state.score+=1
            else:
                st.session_state.score-=0.25
                st.session_state.weak[q["question"]] = 1

        coln1,coln2 = st.columns(2)
        if coln1.button("Prev") and st.session_state.index>0:
            st.session_state.index-=1
        if coln2.button("Next") and st.session_state.index<len(st.session_state.exam_q)-1:
            st.session_state.index+=1

        st.write("Score:", st.session_state.score)

    # ===== EXTRA =====
    st.markdown("## 📊 Weak Topics")
    st.write(st.session_state.weak)

    if st.button("🧠 Smart Revision"):
        st.write(ai(format_prompt(f"Teach weak topics: {list(st.session_state.weak.keys())}")))

    if st.button("📂 PYQ"):
        st.write(ai(format_prompt("Give last 10 year repeated questions")))

    if st.button("📅 Study Plan"):
        st.write(ai(format_prompt("Create daily study plan")))

    score = st.number_input("Score for rank prediction")
    if st.button("📊 Rank"):
        st.write(ai(f"Predict rank for score {score}"))
