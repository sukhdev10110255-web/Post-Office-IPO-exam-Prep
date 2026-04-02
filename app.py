import streamlit as st
import os
import PyPDF2
from gtts import gTTS
import tempfile
from cerebras.cloud.sdk import Cerebras

# ================= CONFIG =================
st.set_page_config(page_title="Avyan LDCE v19", layout="wide")

# ================= SESSION =================
defaults = {
    "topic": "",
    "pdf_text": "",
    "mcqs": [],
    "weak": {},
    "messages": [],
    "theme": "Light",
    "lang": "Bilingual"
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ================= THEME =================
if st.session_state.theme=="Dark":
    st.markdown("<style>body{background:#111;color:white}</style>",unsafe_allow_html=True)

# ================= AI =================
def ai(prompt):
    try:
        client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
        res = client.chat.completions.create(
            model="llama3.1-8b-instant",
            messages=[{"role":"user","content":prompt}],
            max_tokens=800
        )
        return res.choices[0].message.content
    except:
        return None

# ================= PDF =================
def pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() for p in reader.pages])

# ================= NOTES =================
def notes(topic):
    res = ai(f"Explain {topic} for LDCE exam in Hindi and English")
    return res if res else f"Basic notes for {topic}"

# ================= MCQ =================
def mcq(topic):
    res = ai(f"Generate 5 MCQs on {topic}")
    if res:
        qs=[]
        lines=res.split("\n")
        q={}
        for l in lines:
            if l.startswith("Q"):
                if q: qs.append(q)
                q={"q":l,"opt":[]}
            elif l.startswith(("A","B","C","D")):
                q["opt"].append(l)
            elif "Answer" in l:
                q["ans"]=l
        if q: qs.append(q)
        return qs
    return [{"q":f"What is {topic}?","opt":["A","B","C","D"],"ans":"A"}]

# ================= WEAK =================
def track(topic,correct):
    if topic not in st.session_state.weak:
        st.session_state.weak[topic]=[0,0]
    st.session_state.weak[topic][1]+=1
    if correct: st.session_state.weak[topic][0]+=1

def weak_list():
    return [t for t,v in st.session_state.weak.items() if v[0]/v[1]<0.6]

# ================= UI =================
st.title("🚀 Avyan LDCE IP Masterpiece v19")

# ---------- SETTINGS ----------
with st.sidebar:
    st.selectbox("Theme",["Light","Dark"],key="theme")
    st.selectbox("Language",["Bilingual","English","Hindi"],key="lang")

# ---------- SEARCH ----------
st.subheader("🌐 Smart Search")
col1,col2=st.columns([4,1])
q=col1.text_input("Search topic")
engine=col2.selectbox("",["Google","Bing","DuckDuckGo"])

if st.button("Search"):
    url={
        "Google":f"https://www.google.com/search?q={q}",
        "Bing":f"https://bing.com/search?q={q}",
        "DuckDuckGo":f"https://duckduckgo.com/?q={q}"
    }
    st.markdown(url[engine])

# ---------- PDF ----------
file=st.file_uploader("Upload PDF")
if file:
    st.session_state.pdf_text=pdf_text(file)

# ---------- PAPER ----------
paper=st.selectbox("Select Paper",["Paper1","Paper2","Paper3","Paper4"])
topic=st.text_input("Enter Topic")

if st.button("Set Topic"):
    st.session_state.topic=topic

# ---------- NOTES ----------
if st.button("Generate Notes"):
    st.write(notes(st.session_state.topic))

# ---------- CHAT ----------
msg=st.text_input("Ask AI")
if msg:
    st.write(ai(msg) or "Add API")

# ---------- MCQ ----------
if st.button("Generate MCQ"):
    st.session_state.mcqs=mcq(st.session_state.topic)

for i,q in enumerate(st.session_state.mcqs):
    st.write(q["q"])
    ans=st.radio("Choose",q["opt"],key=i)
    if st.button(f"Check {i}"):
        if q["ans"][0] in ans:
            st.success("Correct")
            track(st.session_state.topic,True)
        else:
            st.error(q["ans"])
            track(st.session_state.topic,False)

# ---------- WEAK ----------
st.subheader("Weak Topics")
for w in weak_list():
    st.write("❌",w)

# ---------- REVISION ----------
if st.button("Smart Revision"):
    for w in weak_list():
        st.write(notes(w))
