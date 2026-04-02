import streamlit as st
import os
import json
import re
import tempfile
import time
from datetime import datetime
import random
from gtts import gTTS
import PyPDF2
from cerebras.cloud.sdk import Cerebras
import requests

# ==================== CONFIG ====================
st.set_page_config(page_title="Avyan LDCE v18.0", layout="wide", initial_sidebar_state="expanded")

# ==================== AI FUNCTION ====================
def ai(prompt, system_prompt="You are a helpful LDCE exam tutor."):
    """Cerebras AI function - properly working"""
    try:
        client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY", st.session_state.get("cerebras_key", "")))
        res = client.chat.completions.create(
            model="llama3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return res.choices[0].message.content
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# ==================== SIDEBAR SETTINGS ====================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=80)
    st.title("⚙️ Settings")
    
    # Theme Selector - Optional
    theme_option = st.selectbox("🎨 Choose Theme", ["Light 🌞", "Dark 🌙", "System Default"])
    
    lang = st.selectbox("🌐 Language", ["Bilingual", "English", "Hindi"])
    
    st.markdown("---")
    st.subheader("🔑 Cerebras AI Key")
    cerebras_input = st.text_input("Cerebras API Key", type="password", 
                                   help="Get from https://cloud.cerebras.ai")
    if cerebras_input:
        st.session_state.cerebras_key = cerebras_input
        os.environ["CEREBRAS_API_KEY"] = cerebras_input
    
    if not st.session_state.get("cerebras_key"):
        st.warning("⚠️ Please add Cerebras API Key for AI features")
    else:
        st.success("✅ Cerebras AI Ready")
    
    st.markdown("---")
    st.caption("Avyan LDCE v18.0 – Full System with Cerebras AI")

# ==================== APPLY THEME (OPTIONAL) ====================
def apply_theme():
    """Apply selected theme"""
    theme = st.session_state.get('theme_option', 'Light 🌞')
    
    if theme == "Dark 🌙":
        st.markdown("""
            <style>
            /* Dark Theme */
            .stApp {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #ffffff;
            }
            .card {
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 20px;
                margin: 10px 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
            }
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
                border-color: rgba(255, 255, 255, 0.2);
            }
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .stTextInput > div > div > input {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
            }
            .stSelectbox > div > div {
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #ffffff;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .stMarkdown {
                color: #e0e0e0;
            }
            </style>
        """, unsafe_allow_html=True)
    
    elif theme == "Light 🌞":
        st.markdown("""
            <style>
            /* Light Theme */
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                color: #2c3e50;
            }
            .card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 20px;
                margin: 10px 0;
                border: 1px solid rgba(0, 0, 0, 0.05);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            }
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .stTextInput > div > div > input {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
            h1, h2, h3, h4, h5, h6 {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            </style>
        """, unsafe_allow_html=True)
    
    else:  # System Default
        st.markdown("""
            <style>
            /* System Default Theme - Clean & Modern */
            .stApp {
                background: #f8f9fa;
            }
            .card {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
                border: 1px solid #e9ecef;
            }
            .card:hover {
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
                transform: translateY(-2px);
            }
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }
            h1 {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.5rem;
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)

# Apply theme based on selection
if 'theme_option' not in st.session_state:
    st.session_state.theme_option = theme_option
apply_theme()

# ==================== SESSION STATE ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "weak_topics" not in st.session_state:
    st.session_state.weak_topics = {}
if "exam_score" not in st.session_state:
    st.session_state.exam_score = 0
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""
if "cerebras_key" not in st.session_state:
    st.session_state.cerebras_key = ""

# ==================== PDF FUNCTIONS ====================
def extract_pdf_text(uploaded_file):
    """Extract text from uploaded PDF"""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"PDF extraction error: {e}")
        return ""

# ==================== NOTES GENERATION ====================
def generate_notes(topic, pdf_text=""):
    """Generate notes using Cerebras AI"""
    if not st.session_state.get("cerebras_key"):
        return fallback_notes(topic)
    
    context = pdf_text[:2000] if pdf_text else ""
    prompt = f"""Write comprehensive study notes on '{topic}' for LDCE exam.

Requirements:
- Key definitions and concepts
- Important rules and sections
- Practical examples
- Exam tips
- Summary

Topic: {topic}
Context: {context}

Generate detailed notes with headings and bullet points:"""
    
    response = ai(prompt, "You are an expert LDCE tutor creating clear study materials.")
    return response if response else fallback_notes(topic)

def fallback_notes(topic):
    return f"""
## 📚 {topic} - Study Notes

### Key Concepts
- **Definition**: Important topic for LDCE examination
- **Relevance**: Frequently tested in Paper 1-4
- **Weightage**: High priority area

### Important Points
1. Master the fundamentals first
2. Practice previous year questions
3. Focus on recent amendments
4. Regular revision is essential

### Exam Tips
✅ Focus on definitions
✅ Practice numerical problems
✅ Review case studies
✅ Take mock tests regularly
"""

# ==================== MCQ GENERATION ====================
def generate_mcq(topic, num=5):
    """Generate MCQs using Cerebras AI"""
    if not st.session_state.get("cerebras_key"):
        return fallback_mcqs(topic, num)
    
    prompt = f"""Generate {num} multiple-choice questions for LDCE exam on '{topic}'.

Format each:
Q: [Question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
Answer: [Letter]

Make questions exam-relevant:"""
    
    response = ai(prompt, "You are an LDCE exam question setter.")
    
    if response:
        mcqs = []
        lines = response.split('\n')
        current_q = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_q:
                    mcqs.append(current_q)
                current_q = {'question': line[2:].strip(), 'options': []}
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                current_q['options'].append(line[2:].strip())
            elif line.startswith('Answer:'):
                current_q['answer'] = line[7:].strip()
        
        if current_q:
            mcqs.append(current_q)
        
        return mcqs if mcqs else fallback_mcqs(topic, num)
    
    return fallback_mcqs(topic, num)

def fallback_mcqs(topic, num):
    return [
        {"question": f"What is the main objective of {topic}?",
         "options": ["Service Delivery", "Revenue Generation", "Customer Satisfaction", "All of above"],
         "answer": "All of above"},
        {"question": f"Which section deals with {topic}?",
         "options": ["Section 5", "Section 12", "Section 18", "Section 25"],
         "answer": "Section 12"},
        {"question": f"Who is the authority for {topic}?",
         "options": ["Minister", "Secretary", "Director", "Commissioner"],
         "answer": "Secretary"}
    ][:num]

# ==================== TRACKING ====================
def track_weakness(topic, correct):
    if topic not in st.session_state.weak_topics:
        st.session_state.weak_topics[topic] = {"total": 0, "correct": 0}
    st.session_state.weak_topics[topic]["total"] += 1
    if correct:
        st.session_state.weak_topics[topic]["correct"] += 1

def get_weak_topics():
    weak = []
    for topic, stats in st.session_state.weak_topics.items():
        if stats["total"] > 0 and (stats["correct"] / stats["total"]) < 0.6:
            weak.append(topic)
    return weak

# ==================== VOICE ====================
def speak_text(text):
    try:
        tts = gTTS(text=text[:500], lang="hi" if lang == "Hindi" else "en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

# ==================== RANK PREDICTION ====================
def predict_rank(score):
    if score >= 90: return "1-50 (Excellent)"
    elif score >= 80: return "51-200 (Very Good)"
    elif score >= 70: return "201-500 (Good)"
    elif score >= 60: return "501-1000 (Average)"
    else: return ">1000 (Need Improvement)"

# ==================== MAIN UI ====================
st.title("🚀 Avyan LDCE IP Masterpiece v18.0")
st.caption("Full System – Cerebras AI Powered | LDCE Exam Preparation")

# Check API Key Status
if not st.session_state.get("cerebras_key"):
    st.info("💡 Tip: Add your Cerebras API Key in the sidebar to enable all AI features")

# ==================== SMART SEARCH ====================
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🌐 Smart Search")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("Search topic / act / rules", key="search_input", 
                                     placeholder="e.g., Indian Post Office Act, RTI Act...")
    with col2:
        search_engine = st.selectbox("Engine", ["Google", "Bing", "DuckDuckGo"])
    
    if st.button("🔍 Search", use_container_width=True):
        if search_query:
            if search_engine == "Google":
                url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            elif search_engine == "Bing":
                url = f"https://www.bing.com/search?q={search_query.replace(' ', '+')}"
            else:
                url = f"https://duckduckgo.com/?q={search_query.replace(' ', '+')}"
            st.markdown(f"[🔗 Open {search_engine} Results]({url})")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== PDF UPLOAD ====================
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📄 PDF Upload")
    uploaded_file = st.file_uploader("Upload PDF for context", type="pdf", 
                                     help="Upload study materials, notes, or previous papers")
    if uploaded_file:
        with st.spinner("Extracting text..."):
            st.session_state.pdf_text = extract_pdf_text(uploaded_file)
            st.success(f"✅ Extracted {len(st.session_state.pdf_text)} characters")
            if len(st.session_state.pdf_text) > 0:
                st.info(f"Preview: {st.session_state.pdf_text[:200]}...")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== PAPER & TOPIC ====================
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📚 Paper & Topic Selection")
    
    col1, col2 = st.columns(2)
    with col1:
        paper = st.selectbox("Select Paper", ["Paper 1", "Paper 2", "Paper 3", "Paper 4"])
    
    syllabus = {
        "Paper 1": ["Post Office Act 2023", "Savings Bank Rules", "Indian Postal Rules", "RTI Act 2005", "Consumer Protection Act"],
        "Paper 2": ["Mail Manual Vol I", "Mail Manual Vol II", "Parcel Rules", "Money Order Rules", "Speed Post Rules"],
        "Paper 3": ["English Grammar", "Essay Writing", "Comprehension", "Precis Writing", "Official Correspondence"],
        "Paper 4": ["Accounts", "Statistics", "General Knowledge", "Computer Awareness", "Current Affairs"]
    }
    
    with col2:
        topic_options = syllabus.get(paper, [])
        topic_select = st.selectbox("Choose from syllabus", topic_options)
    
    topic_input = st.text_input("Or custom topic", placeholder="e.g., Digital India, RTI Act, Banking Rules")
    final_topic = topic_input if topic_input else topic_select
    
    if st.button("✅ Set Topic", use_container_width=True, type="primary"):
        st.session_state.current_topic = final_topic
        st.success(f"📌 Current topic set to: **{final_topic}**")
        st.balloons()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== NOTES & VOICE ====================
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📘 Study Notes")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Generate Notes", use_container_width=True):
            if st.session_state.current_topic:
                with st.spinner(f"Generating notes on {st.session_state.current_topic}..."):
                    notes = generate_notes(st.session_state.current_topic, st.session_state.pdf_text)
                    if notes:
                        st.session_state.generated_notes = notes
                        st.markdown(notes)
                    else:
                        st.error("Failed to generate notes. Check API key.")
            else:
                st.warning("Please select a topic first")
    
    with col2:
        if "generated_notes" in st.session_state:
            if st.button("🔊 Voice", use_container_width=True):
                audio_file = speak_text(st.session_state.generated_notes)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== AI CHAT ====================
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💬 AI Discussion")
    
    # Display chat history
    for msg in st.session_state.messages[-10:]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    user_q = st.chat_input("Ask anything about the current topic...")
    if user_q:
        st.session_state.messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.write(user_q)
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                prompt = f"Current Topic: {st.session_state.current_topic}\n\nUser Question: {user_q}\n\nProvide a detailed, helpful answer for LDCE exam preparation:"
                response = ai(prompt, "You are an expert LDCE tutor. Provide clear, detailed answers with examples.")
                if response:
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.write("Please add Cerebras API key in sidebar for AI responses.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== MCQ TEST ====================
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 MCQ Test")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Generate MCQs", use_container_width=True):
            if st.session_state.current_topic:
                with st.spinner("Generating MCQs..."):
                    st.session_state.mcq_set = generate_mcq(st.session_state.current_topic, 5)
                    st.success(f"Generated {len(st.session_state.mcq_set)} questions")
            else:
                st.warning("Select topic first")
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            if "mcq_set" in st.session_state:
                del st.session_state.mcq_set
    
    if "mcq_set" in st.sess
