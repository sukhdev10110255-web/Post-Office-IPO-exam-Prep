import streamlit as st
import os, json, re, time, datetime
import PyPDF2
from groq import Groq

# ================= CONFIG =================
st.set_page_config(page_title="🔥 IPO EXAM AI V4", layout="wide")

# ================= UI =================
st.markdown("""
<style>
.stApp {background:linear-gradient(135deg,#0f0f0f,#1c1c1c); color:white;}
h1,h2,h3 {color:#e50914;}
.stButton button {background:#e50914;color:white;border-radius:8px;}
.card {background:#1e1e1e;padding:20px;border-radius:12px;margin:10px 0;}
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
    "daily_plan":"", "history":[]
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ================= HEADER =================
st.title("🔥 IPO 2026 AI MASTER SYSTEM (V4)")
st.markdown("📚 Notes | 🧠 MCQ | 📝 Exam | 📊 PYQ | 🎯 Weak AI | 📅 Planner")

# ================= INPUT =================
col1,col2 = st.columns(2)

with col1:
    topic = st.text_input("🎯 Topic")

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
mode = st.selectbox("Mode",[
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
        raw=ask(f"""
        Generate {num_q} MCQ in {lang}
        JSON: question, options, correct_answer
        {content}
        """)
        st.write(raw)

# ================= EXAM =================
if mode=="📝 Exam Simulator":

    if st.button("Start Exam"):
        raw=ask(f"""
        Generate {num_q} MCQ JSON
        IPO exam level {lang}
        """)
        try:
            data=json.loads(re.search(r'\{.*\}',raw,re.DOTALL).group())
            st.session_state.quiz=data["questions"]
            st.session_state.index=0
            st.session_state.score=0
            st.session_state.start_time=time.time()
        except:
            st.error("Parsing error")

    # TIMER
    if st.session_state.start_time:
        elapsed=time.time()-st.session_state.start_time
        rem=int(timer_min*60-elapsed)
        st.warning(f"⏱️ Time Left: {rem//60}:{rem%60}")

    # QUIZ
    if st.session_state.quiz:
        q=st.session_state.quiz[st.session_state.index]
        st.markdown(f"<div class='card'><h3>Q{st.session_state.index+1}</h3>{q['question']}</div>",unsafe_allow_html=True)

        ans=st.radio("Select",q["options"])

        if st.button("Submit"):
            if ans==q["correct_answer"]:
                st.session_state.score+=1
                st.success("Correct")
            else:
                if negative:
                    st.session_state.score-=0.25
                st.error(f"Wrong | {q['correct_answer']}")

                # 🔥 weak topic detect
                topic_name=ask(f"Topic of this question: {q['question']}")
                st.session_state.weak_topics.append(topic_name)

        if st.button("Next"):
            if st.session_state.index < len(st.session_state.quiz)-1:
                st.session_state.index+=1
            else:
                st.success("Exam Finished")

    # RESULT
    if st.session_state.quiz and st.session_state.index==len(st.session_state.quiz)-1:
        st.metric("Score",st.session_state.score)

# ================= PYQ =================
if mode=="📊 PYQ Analyzer":
    if st.button("Analyze PYQ"):
        st.write(ask("""
        Analyze last 10 year IPO exam
        Give repeated topics, patterns, scoring areas
        """))

# ================= DAILY PLAN =================
if mode=="📅 Daily Plan":
    if st.button("Generate Plan"):
        plan=ask("Create daily IPO exam study plan")
        st.session_state.daily_plan=plan
        st.write(plan)

    if st.session_state.weak_topics:
        st.warning("⚠️ Revise weak topics today!")

# ================= WEAK TRAINER =================
if mode=="🎯 Weak Topic Trainer":
    if st.session_state.weak_topics:
        topics=list(set(st.session_state.weak_topics))

        for t in topics:
            with st.expander(f"⚠️ {t}"):

                if st.button(f"Learn {t}"):
                    st.write(ask(f"Teach {t} simply Hindi+English"))

                if st.button(f"Practice {t}"):
                    st.write(ask(f"Give 5 MCQ on {t}"))

                if st.button(f"Revise {t}"):
                    st.write(ask(f"Quick revision {t}"))
    else:
        st.info("No weak topics yet")

# ================= FOOTER =================
st.markdown("---")
st.caption("🔥 Powered by AI | IPO 2026 Prep System")
