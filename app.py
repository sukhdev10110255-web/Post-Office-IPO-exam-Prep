import streamlit as st
import os, json, re, time
import PyPDF2
from groq import Groq

# ================= CONFIG =================
st.set_page_config(page_title="📘 IPO AI COACH", layout="wide")

# ================= PREMIUM LIGHT UI =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#eef2f7,#dbeafe);
}

/* Chat bubbles */
.chat-user {
    background:#2563eb;
    color:white;
    padding:10px 15px;
    border-radius:15px;
    margin:5px;
    text-align:right;
}
.chat-ai {
    background:white;
    padding:10px 15px;
    border-radius:15px;
    margin:5px;
    box-shadow:0 2px 6px rgba(0,0,0,0.1);
}

/* Cards */
.card {
    background:white;
    padding:20px;
    border-radius:12px;
    margin:10px 0;
    box-shadow:0 4px 10px rgba(0,0,0,0.08);
}

/* Buttons */
.stButton button {
    background:#2563eb;
    color:white;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# ================= GROQ =================
@st.cache_resource
def client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        st.error("Add GROQ_API_KEY")
        st.stop()
    return Groq(api_key=key)

def ask(prompt):
    res = client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=0.7
    )
    return res.choices[0].message.content

# ================= PDF =================
def read_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    text=""
    for p in pdf.pages:
        if p.extract_text():
            text+=p.extract_text()
    return text

# ================= SESSION =================
defaults = {
    "quiz":[], "index":0, "score":0,
    "start_time":None, "weak_topics":[],
    "study_content":"", "chat":[]
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ================= HEADER =================
st.title("📘 IPO 2026 AI COACH (ChatGPT Style)")
st.markdown("📚 Study | 💬 Chat | 🧠 MCQ | 📝 Exam | 🎯 Weak AI")

# ================= INPUT =================
col1,col2 = st.columns(2)

with col1:
    topic = st.text_input("🎯 Enter Topic")

with col2:
    pdf = st.file_uploader("📄 Upload PDF", type="pdf")

content=""
if pdf:
    content=read_pdf(pdf)
elif topic:
    content=topic

# ================= MODE =================
mode = st.selectbox("Select Mode",[
    "📖 Study + Chat",
    "🧠 MCQ Practice",
    "📝 Exam Simulator",
    "🎯 Weak Topics"
])

# ================= STUDY + CHAT =================
if mode=="📖 Study + Chat":

    if content and st.button("Generate Notes"):
        notes = ask(f"""
        Create structured notes in Hindi + English.
        {content}
        """)
        st.session_state.study_content = notes

    # SHOW NOTES
    if st.session_state.study_content:
        st.markdown("### 📖 Notes")
        st.markdown(f"<div class='card'>{st.session_state.study_content}</div>", unsafe_allow_html=True)

    # CHAT UI
    st.markdown("## 💬 Ask Doubts")

    user_input = st.text_input("Type your question...")

    if st.button("Send") and user_input:
        st.session_state.chat.append(("user", user_input))

        # typing animation
        placeholder = st.empty()
        placeholder.markdown("🤖 Typing...")

        reply = ask(f"""
        Context:
        {st.session_state.study_content}

        Question:
        {user_input}

        Answer in Hindi + English
        """)

        placeholder.empty()
        st.session_state.chat.append(("ai", reply))

    # DISPLAY CHAT
    for role,msg in st.session_state.chat:
        if role=="user":
            st.markdown(f"<div class='chat-user'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-ai'>{msg}</div>", unsafe_allow_html=True)

# ================= MCQ =================
if mode=="🧠 MCQ Practice":
    if content and st.button("Generate MCQ"):
        st.write(ask(f"Generate MCQ Hindi+English JSON:\n{content}"))

# ================= EXAM =================
if mode=="📝 Exam Simulator":

    if st.button("Start Exam"):
        raw=ask("Generate 10 MCQ JSON IPO exam")
        try:
            data=json.loads(re.search(r'\{.*\}',raw,re.DOTALL).group())
            st.session_state.quiz=data["questions"]
            st.session_state.index=0
            st.session_state.score=0
            st.session_state.start_time=time.time()
        except:
            st.error("Error")

    if st.session_state.quiz:
        q=st.session_state.quiz[st.session_state.index]
        st.markdown(f"<div class='card'><b>Q{st.session_state.index+1}</b><br>{q['question']}</div>",unsafe_allow_html=True)

        ans=st.radio("Select",q["options"])

        if st.button("Submit"):
            if ans==q["correct_answer"]:
                st.session_state.score+=1
                st.success("Correct")
            else:
                st.error(f"Wrong | {q['correct_answer']}")

                topic_name=ask(f"Topic: {q['question']}")
                st.session_state.weak_topics.append(topic_name)

        if st.button("Next"):
            if st.session_state.index < len(st.session_state.quiz)-1:
                st.session_state.index+=1
            else:
                st.success("Finished")

    if st.session_state.quiz:
        st.metric("Score",st.session_state.score)

# ================= WEAK =================
if mode=="🎯 Weak Topics":
    if st.session_state.weak_topics:
        for t in set(st.session_state.weak_topics):
            with st.expander(f"⚠️ {t}"):
                st.write(ask(f"Teach {t} Hindi + English"))
    else:
        st.info("No weak topics yet")

# ================= FOOTER =================
st.markdown("---")
st.caption("🚀 IPO AI Coach | ChatGPT Style UI")
