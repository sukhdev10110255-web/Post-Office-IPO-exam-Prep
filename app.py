import streamlit as st
import os, re, json
import PyPDF2
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v14.0", layout="wide")

# ================= AI =================
def ai(prompt):
    try:
        client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
        res = client.chat.completions.create(
            model="llama3.1-8b-instant",
            messages=[{"role":"user","content":prompt}],
            max_tokens=1000
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# ================= PDF =================
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() or "" for p in reader.pages])[:10000]

# ================= SESSION =================
defaults = {
    "current_topic":"",
    "search_query":"",
    "questions":[],
    "weak":{},
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================= UI =================
st.title("🚀 Avyan LDCE IP Exam Masterpiece v14.0")

# ================= SEARCH =================
st.subheader("🌐 Smart Browser")

col1, col2 = st.columns([4,1])

with col1:
    query = st.text_input("🔍 Search (Acts / Rules / PDF)", key="search_box")

with col2:
    if st.button("Search"):
        st.session_state.search_query = query

query = st.session_state.search_query

# 🔗 Search links
if query:
    st.markdown(f"[🔎 Google](https://www.google.com/search?q={query})")
    st.markdown(f"[🧠 Bing](https://www.bing.com/search?q={query})")
    st.markdown(f"[📚 DuckDuckGo](https://duckduckgo.com/?q={query})")

    if st.button("📄 Find PDFs"):
        st.markdown(f"[📥 PDF Results](https://www.google.com/search?q={query}+filetype:pdf)")

    if st.button("🤖 Explain Topic"):
        st.write(ai(f"Explain in Hindi and English:\n{query}"))

    if st.button("📖 Use for Study"):
        st.session_state.current_topic = query
        st.session_state.questions = []
        st.success("Topic set for study!")

# ================= INPUT =================
st.subheader("📚 Study Input")

topic = st.text_area("Enter Topic")

if st.button("🔎 Enter Topic"):
    st.session_state.current_topic = topic
    st.session_state.questions = []
    st.success("Topic updated!")

pdf = st.file_uploader("Upload PDF")
if pdf:
    st.session_state.current_topic = read_pdf(pdf)
    st.success("PDF loaded!")

# ================= STUDY =================
st.subheader("🎯 Study Modes")

col1, col2, col3, col4 = st.columns(4)

# ---------- LEARN ----------
if col1.button("📖 Learn"):
    topic = st.session_state.current_topic
    if topic:
        st.write(ai(f"Explain for exam in Hindi and English:\n{topic}"))
    else:
        st.warning("Enter topic first")

# ---------- CHAT ----------
if col2.button("💬 Chat"):
    q = st.text_input("Ask doubt")
    if q:
        st.write(ai(q))

# ---------- MCQ ----------
if col3.button("📝 MCQ"):
    topic = st.session_state.current_topic
    if topic:
        res = ai(f"Generate 5 MCQs in JSON:\n{topic}")
        try:
            data = json.loads(re.search(r'\{.*\}', res, re.DOTALL).group())
            st.session_state.questions = data["questions"]
        except:
            st.error("MCQ generation failed")

# ---------- EXAM ----------
if col4.button("🧪 Final Exam"):
    st.session_state.score = 0

# ================= MCQ DISPLAY =================
if st.session_state.questions:
    st.subheader("📝 MCQ Practice")

    for i,q in enumerate(st.session_state.questions):
        st.write(f"Q{i+1}: {q['question']}")

        ans = st.radio("Choose", q["options"], key=f"q{i}")

        if st.button(f"Check {i}"):
            if ans == q["correct_answer"]:
                st.success("✅ Correct")
            else:
                st.error("❌ Wrong")
                st.session_state.weak[q["question"]] = q["correct_answer"]

# ================= WEAK =================
st.subheader("📉 Weak Topics")

if st.session_state.weak:
    for w in st.session_state.weak:
        with st.expander(w):
            st.write("Correct:", st.session_state.weak[w])
else:
    st.success("No weak topics yet!")

if st.button("🧠 Smart Revision"):
    weak_list = list(st.session_state.weak.keys())
    if weak_list:
        st.write(ai(f"Teach these weak topics:\n{weak_list}"))
    else:
        st.warning("No weak topics")
