import streamlit as st
import os, json, re
import PyPDF2
from datetime import datetime
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE IP v14.0", layout="wide")

# ================= SETTINGS =================
theme = st.selectbox("🎨 Theme", ["Light","Dark"])
lang = st.selectbox("🌐 Language", ["Bilingual","English","Hindi"])

if theme == "Dark":
    st.markdown("<style>.stApp{background:#0e1117;color:white}</style>", unsafe_allow_html=True)

def format_prompt(text):
    if lang=="English": return f"Answer in English:\n{text}"
    elif lang=="Hindi": return f"Answer in Hindi:\n{text}"
    else: return f"Answer in English and Hindi:\n{text}"

# ================= AI =================
def ai(prompt):
    try:
        client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
        res = client.chat.completions.create(
            model="llama3.1-8b",
            messages=[{"role":"user","content":prompt}],
            max_tokens=1200
        )
        return res.choices[0].message.content
    except:
        return "AI Error"

# ================= PDF =================
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() or "" for p in reader.pages])[:15000]

# ================= SESSION =================
for key in ["page","questions","weak","exam_q","index","score","chat","content","saved"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["questions","exam_q","chat","saved"] else {} if key=="weak" else 0 if key in ["index","score"] else "" if key=="content" else "home"

# ================= HOME =================
if st.session_state.page == "home":
    st.title("🚀 Avyan LDCE IP Exam Masterpiece v14.0")

    cols = st.columns(4)
    for i,p in enumerate(["Paper 1","Paper 2","Paper 3","Paper 4"]):
        if cols[i].button(p):
            st.session_state.paper = p
            st.session_state.page = "mode"

# ================= MODE =================
elif st.session_state.page == "mode":
    st.title(st.session_state.paper)

    c1,c2,c3 = st.columns(3)
    if c1.button("🔍 Topic"): st.session_state.input="topic"; st.session_state.page="study"
    if c2.button("📄 PDF"): st.session_state.input="pdf"; st.session_state.page="study"
    if c3.button("🤖 AI Course"): st.session_state.input="ai"; st.session_state.page="study"

# ================= STUDY =================
elif st.session_state.page == "study":

    st.title("📚 Study Dashboard")

    # ---------- Topic ----------
    if st.session_state.input == "topic":
        topic = st.text_area("Enter Topic", value=st.session_state.content)
        if st.button("🔎 Enter Topic"):
            st.session_state.content = topic

    # ---------- PDF ----------
    elif st.session_state.input == "pdf":
        pdf = st.file_uploader("Upload PDF")
        if pdf:
            st.session_state.content = read_pdf(pdf)

    # ---------- AI ----------
    elif st.session_state.input == "ai":
        if st.button("Generate AI Syllabus"):
            st.session_state.content = ai(f"Generate LDCE syllabus for {st.session_state.paper}")

    content = st.session_state.content

    # ================= SMART BROWSER =================
    st.markdown("## 🌐 Smart Browser")

    query = st.text_input("🔍 Search Anything (Acts / Rules / PDF)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"[🔎 Google](https://www.google.com/search?q={query})")

    with col2:
        st.markdown(f"[🧠 Bing](https://www.bing.com/search?q={query})")

    with col3:
        st.markdown(f"[📚 DuckDuckGo](https://duckduckgo.com/?q={query})")

    if st.button("📄 Find PDFs"):
        st.markdown(f"[📥 Open PDF Results](https://www.google.com/search?q={query}+filetype:pdf)")

    if st.button("🤖 Explain Topic"):
        st.write(ai(format_prompt(query)))

    if st.button("💾 Save Topic Offline"):
        st.session_state.saved.append(query)
        st.success("Saved!")

    # ================= LEARNING =================
    st.markdown("## 🎯 Study Modes")

    col1,col2,col3,col4,col5 = st.columns(5)

    if col1.button("📖 Learn"):
        st.write(ai(format_prompt(f"Explain: {content}")))

    if col2.button("💬 Chat"):
        q = st.text_input("Ask Question")
        if q:
            st.session_state.chat.append(("user", q))
            reply = ai(q)
            st.session_state.chat.append(("ai", reply))

    for role,msg in st.session_state.chat:
        st.write(f"{role}: {msg}")

    # ================= MCQ =================
    if col3.button("📝 MCQ"):
        st.session_state.questions = [{
            "question":"Sample Question",
            "options":["A","B","C","D"],
            "correct_answer":"A"
        }]

    for i,q in enumerate(st.session_state.questions):
        st.write(q["question"])
        ans = st.radio("Choose", q["options"], key=f"mcq{i}")

        if st.button(f"Check {i}"):
            if ans == q["correct_answer"]:
                st.success("Correct")
            else:
                st.error("Wrong")
                st.session_state.weak[q["question"]] = 1

    # ================= EXAM =================
    if col5.button("🧪 Final Exam"):
        st.session_state.exam_q = st.session_state.questions
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.start = datetime.now()

    if st.session_state.exam_q:
        q = st.session_state.exam_q[st.session_state.index]
        st.write(q["question"])

        ans = st.radio("Answer", q["options"], key="exam")

        if st.button("Submit"):
            if ans == q["correct_answer"]:
                st.session_state.score += 1
            else:
                st.session_state.score -= 0.25

        st.write("Score:", st.session_state.score)

    # ================= WEAK =================
    st.markdown("## 📊 Weak Topics")
    st.write(st.session_state.weak)

    if st.button("🧠 Smart Revision"):
        st.write(ai(format_prompt(f"Teach weak topics: {list(st.session_state.weak.keys())}")))

    # ================= OFFLINE =================
    st.markdown("## 📂 Offline Saved Topics")
    for s in st.session_state.saved:
        st.write("📌", s)
