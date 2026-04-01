import streamlit as st
import os
import PyPDF2
import json
import re

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="📚 LDCE AI Prep V5", layout="wide")

st.write("🚀 System Running")

# ========== STYLE ==========
st.markdown("""
<style>
.stApp { background:#f5f7fa; }
h1 { color:#1e3c72; }
.stButton button { background:#1e3c72; color:white; border-radius:8px; }
.question-card { background:white;padding:15px;border-radius:10px;border-left:4px solid #1e3c72; }
</style>
""", unsafe_allow_html=True)

# ========== CLIENT ==========
def get_client():
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        st.error("❌ API key missing")
        return None
    
    try:
        from cerebras.cloud.sdk import Cerebras
        return Cerebras(api_key=api_key)
    except Exception as e:
        st.error(e)
        return None

# ========== SAFE MODEL CALL ==========
def safe_chat(client, prompt, max_tokens=1000):
    models = ["llama3.1-70b", "llama3.1-8b"]  # auto fallback

    for model in models:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[{"role":"user","content":prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return res.choices[0].message.content
        except Exception as e:
            continue

    return "❌ All models failed"

# ========== PDF ==========
def extract_pdf(file):
    text = ""
    pdf = PyPDF2.PdfReader(file)
    for p in pdf.pages:
        t = p.extract_text()
        if t:
            text += t
    return text

# ========== CHUNK ==========
def split_text(text, size=3000):
    return [text[i:i+size] for i in range(0, len(text), size)]

# ========== NOTES ==========
def generate_notes(client, content):
    chunks = split_text(content)
    final_notes = ""

    for chunk in chunks[:5]:  # limit for safety
        prompt = f"""
        Create exam-focused notes in Hindi + English:

        {chunk}
        """
        final_notes += safe_chat(client, prompt, 800) + "\n\n"

    return final_notes

# ========== MCQ ==========
def generate_mcq(client, content, n=5):
    content = content[:8000]

    prompt = f"""
    Generate {n} MCQs.

    Content:
    {content}

    JSON format:
    {{
        "questions":[
            {{
                "question":"",
                "options":["A","B","C","D"],
                "correct_answer":"",
                "explanation":""
            }}
        ]
    }}
    """

    txt = safe_chat(client, prompt, 2000)

    try:
        data = json.loads(re.search(r'\{.*\}', txt, re.DOTALL).group())
        return data["questions"]
    except:
        return []

# ========== SESSION ==========
if "questions" not in st.session_state:
    st.session_state.questions = []
if "notes" not in st.session_state:
    st.session_state.notes = ""
if "index" not in st.session_state:
    st.session_state.index = 0

# ========== UI ==========
st.title("📚 LDCE Inspector Prep AI (V5 PRO)")

col1, col2 = st.columns(2)

with col1:
    topic = st.text_area("Enter Topic")

with col2:
    pdf = st.file_uploader("Upload PDF", type="pdf")

content = ""
if pdf:
    content = extract_pdf(pdf)
elif topic:
    content = topic

client = get_client()

# ========== BUTTONS ==========
col1, col2 = st.columns(2)

with col1:
    if st.button("📝 Generate Notes"):
        if content and client:
            with st.spinner("Generating notes..."):
                st.session_state.notes = generate_notes(client, content)

with col2:
    if st.button("🚀 Generate MCQ"):
        if content and client:
            with st.spinner("Generating MCQ..."):
                st.session_state.questions = generate_mcq(client, content)

# ========== NOTES ==========
if st.session_state.notes:
    st.subheader("📖 Notes")
    st.write(st.session_state.notes)

# ========== MCQ ==========
if st.session_state.questions:
    st.subheader("📝 Mock Test")

    q = st.session_state.questions[st.session_state.index]

    st.markdown(f"""
    <div class="question-card">
    <b>Q{st.session_state.index+1}:</b> {q['question']}
    </div>
    """, unsafe_allow_html=True)

    ans = st.radio("Choose answer", q["options"])

    if st.button("Submit"):
        if ans == q["correct_answer"]:
            st.success("✅ Correct")
        else:
            st.error("❌ Wrong")
            st.write("Correct:", q["correct_answer"])
            st.write(q["explanation"])

    if st.button("Next"):
        if st.session_state.index < len(st.session_state.questions)-1:
            st.session_state.index += 1
