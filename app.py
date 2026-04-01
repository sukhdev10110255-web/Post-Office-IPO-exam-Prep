import streamlit as st
import os, json, re, time
import PyPDF2
from groq import Groq

# ================= CONFIG =================
st.set_page_config(page_title="📘 IPO EXAM AI", layout="wide")

# ================= LIGHT UI =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#f5f7fa,#e4ecf7);
    color:#1e293b;
}
h1,h2,h3 {
    color:#1e3a8a;
}
.stButton button {
    background:#2563eb;
    color:white;
    border-radius:10px;
    padding:10px;
}
.card {
    background:white;
    padding:20px;
    border-radius:12px;
    margin:10px 0;
    box-shadow:0 4px 10px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# ================= GROQ =================
@st.cache_resource
def client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        st.error("Add GROQ_API_KEY in Render")
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
    "daily_plan":""
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ================= HEADER =================
st.title("📘 IPO 2026 AI MASTER PREP SYSTEM")
st.markdown("📚 Notes | 🧠 MCQ | 📝 Exam | 📊 PYQ | 🎯 Weak AI | 📅 Planner")

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

# ================= SETTINGS =================
c1,c2,c3 = st.columns(3)
with c1:
    num_q = st.slider("Questions",5,30,10)
with c2:
    lang = st.selectbox("Language",["English","Hindi","Bilingual"])
with c3:
    timer_min = st.slider("Timer (min)",1,60,10)

negative = st.checkbox("Negative Marking (-0.25)")

# ================= MODE =================
mode = st.selectbox("Select Mode",[
    "📖 Notes",
    "🧠 MCQ Practice",
    "📝 Exam Simulator",
    "📊 PYQ Analyzer",
    "📅 Daily Plan",
    "🎯 Weak Topic Trainer"
])

# ================= NOTES =================
if mode=="📖 Notes":
    if content and st.button("Generate Notes"):
        st.write(ask(f"Explain in {lang}:\n{content}"))

# ================= MCQ =================
if mode=="🧠 MCQ Practice":
    if content and st.button("Generate MCQ"):
        st.write(ask(f"Generate {num_q} MCQ in {lang} JSON:\n{content}"))

# ================= EXAM =================
if mode=="📝 Exam Simulator":

    if st.button("Start Exam"):
        raw=ask(f"Generate {num_q} MCQ JSON IPO exam {lang}")
        try:
            data=json.loads(re.search(r'\{.*\}',raw,re.DOTALL).group())
            st.session_state.quiz=data["questions"]
            st.session_state.index=0
            st.session_state.score=0
            st.session_state.start_time=time.time()
        except:
            st.error("Parsing error")

    if st.session_state.start_time:
        elapsed=time.time()-st.session_state.start_time
        rem=int(timer_min*60-elapsed)
        st.warning(f"⏱️ Time Left: {rem//60}:{rem%60}")

    if st.session_state.quiz:
        q=st.session_state.quiz[st.session_state.index]

        st.markdown(f"<div class='card'><h3>Q{st.session_state.index+1}</h3>{q['question']}</div>",unsafe_allow_html=True)

        ans=st.radio("Select",q["options"])

        if st.button("Submit"):
            if ans==q["correct_answer"]:
                st.session_state.score+=1
                st.success("Correct ✅")
            else:
                if negative:
                    st.session_state.score-=0.25
                st.error(f"Wrong ❌ | {q['correct_answer']}")

                topic_name=ask(f"Topic: {q['question']}")
                st.session_state.weak_topics.append(topic_name)

        if st.button("Next"):
            if st.session_state.index < len(st.session_state.quiz)-1:
                st.session_state.index+=1
            else:
                st.success("Exam Finished")

    if st.session_state.quiz and st.session_state.index==len(st.session_state.quiz)-1:
        st.metric("Score",st.session_state.score)

# ================= PYQ =================
if mode=="📊 PYQ Analyzer":
    if st.button("Analyze"):
        st.write(ask("Analyze IPO exam last 10 years PYQ trends"))

# ================= DAILY PLAN =================
if mode=="📅 Daily Plan":
    if st.button("Generate Plan"):
        plan=ask("Create daily IPO exam study plan")
        st.session_state.daily_plan=plan
        st.write(plan)

    if st.session_state.weak_topics:
        st.warning("⚠️ Revise your weak topics today!")

# ================= WEAK TRAINER =================
if mode=="🎯 Weak Topic Trainer":
    if st.session_state.weak_topics:
        topics=list(set(st.session_state.weak_topics))
        for t in topics:
            with st.expander(f"⚠️ {t}"):

                if st.button(f"📖 Learn {t}"):
                    st.write(ask(f"Teach {t} Hindi + English"))

                if st.button(f"🧠 Practice {t}"):
                    st.write(ask(f"Give MCQ on {t}"))

                if st.button(f"🔁 Revise {t}"):
                    st.write(ask(f"Quick revision {t}"))
    else:
        st.info("No weak topics yet")

# ================= FOOTER =================
st.markdown("---")
st.caption("📘 IPO 2026 AI Prep System | Light UI Version")
