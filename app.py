import streamlit as st
import os
import PyPDF2
from groq import Groq
import json
import re
from typing import List, Dict, Optional

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="📚 LDCE Inspector Posts Exam Prep",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Main container */
    .stApp {
        background: #f8fafc;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1e3c72;
        font-family: 'Segoe UI', 'Poppins', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Buttons */
    .stButton button {
        background: #1e3c72;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background: #2a5298;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30,60,114,0.2);
    }
    
    /* Question cards */
    .question-card {
        background: white;
        border-left: 4px solid #1e3c72;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: #1e3c72;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #1e3c72;
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Content box */
    .content-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        max-height: 500px;
        overflow-y: auto;
        font-size: 1rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ========== GROQ CLIENT ==========
@st.cache_resource
def init_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY")
        except:
            pass
    if not api_key:
        st.error("""
        ❌ **GROQ_API_KEY Not Found!**
        
        Please add your Groq API key:
        - **Render:** Environment variable `GROQ_API_KEY`
        - **Local:** Create `.env` or set environment variable
        
        Get your free key at [console.groq.com](https://console.groq.com)
        """)
        st.stop()
    return Groq(api_key=api_key)

# ========== PDF TEXT EXTRACTION ==========
def extract_text_from_pdf(pdf_file) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text if text else "No text could be extracted from PDF."
    except Exception as e:
        st.error(f"❌ PDF Read Error: {str(e)}")
        return ""

# ========== MCQ GENERATION (BILINGUAL) ==========
def generate_mcq_questions(
    client: Groq,
    content: str,
    num_questions: int,
    topic: Optional[str] = None,
    language: str = "bilingual"
) -> List[Dict]:
    """Generate MCQs in specified language(s)"""
    
    # Language instruction
    lang_instruction = {
        "english": "Generate all questions and options in English only.",
        "hindi": "Generate all questions and options in Hindi only. Use Devanagari script.",
        "bilingual": "Generate each question and its options in both English and Hindi. Format: first English version, then Hindi version separated by a line break. The correct_answer should be in the same language as the question (preferably English). Keep explanations in English."
    }.get(language, "Generate in English.")
    
    prompt = f"""
    You are an expert examiner for the Inspector Posts LDCE exam.
    
    {lang_instruction}
    
    Based on the following content, generate {num_questions} high-quality multiple-choice questions:
    
    Content:
    {content[:7000]}
    
    {"Topic: " + topic if topic else ""}
    
    Return ONLY valid JSON in this exact format:
    {{
        "questions": [
            {{
                "question": "Question text (bilingual if requested)",
                "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                "correct_answer": "A. Option 1 (the exact text of the correct option)",
                "explanation": "Brief explanation (English)"
            }}
        ]
    }}
    
    Rules:
    - Each question must have exactly 4 options.
    - Options must be plausible and challenging.
    - Questions should test understanding of the content.
    - If bilingual, provide both languages clearly.
    - Return ONLY valid JSON.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert MCQ generator. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        response_text = completion.choices[0].message.content
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            questions_data = json.loads(json_match.group())
            return questions_data.get("questions", [])
        return []
    except Exception as e:
        st.error(f"🔥 Generation Error: {str(e)}")
        return []

# ========== ANSWER EVALUATION ==========
def evaluate_answer(client: Groq, question: str, user_answer: str, correct_answer: str, explanation: str) -> Dict:
    prompt = f"""
    Evaluate this answer:
    Question: {question}
    User's Answer: {user_answer}
    Correct Answer: {correct_answer}
    Expected Explanation: {explanation}
    
    Return ONLY JSON:
    {{"is_correct": true/false, "feedback": "Short feedback (max 50 words, in English)"}}
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        response_text = completion.choices[0].message.content
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"is_correct": False, "feedback": "Evaluation failed"}
    except Exception as e:
        return {"is_correct": False, "feedback": f"Error: {str(e)}"}

# ========== SESSION STATE INIT ==========
def init_session():
    defaults = {
        'questions': [],
        'current_question': 0,
        'answers': {},
        'results': {},
        'test_started': False,
        'content': None,
        'topic': None,
        'pdf_text': None,
        'language': 'bilingual',
        'num_questions': 10
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ========== MAIN APP ==========
def main():
    init_session()
    
    # Header
    st.title("📚 LDCE Inspector Posts Exam Preparation")
    st.markdown("### AI-Powered MCQ Generator & Mock Test")
    
    # Tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["📖 Reading Material", "✍️ Generate Test", "📝 Mock Test"])
    
    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Language selection
        language = st.selectbox(
            "Question Language",
            ["bilingual", "english", "hindi"],
            format_func=lambda x: {
                "bilingual": "🇮🇳 Bilingual (English + Hindi)",
                "english": "🇬🇧 English Only",
                "hindi": "🇮🇳 Hindi Only"
            }.get(x, x),
            index=0
        )
        st.session_state.language = language
        
        # Number of questions
        num_questions = st.slider("Number of Questions", 3, 20, 10)
        st.session_state.num_questions = num_questions
        
        st.divider()
        
        # Input method
        input_method = st.radio(
            "Input Method",
            ["📄 Upload PDF", "✏️ Enter Topic"],
            horizontal=True
        )
        
        content = None
        topic = None
        
        if input_method == "📄 Upload PDF":
            uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
            if uploaded_file:
                with st.spinner("Extracting text from PDF..."):
                    pdf_text = extract_text_from_pdf(uploaded_file)
                    st.session_state.pdf_text = pdf_text
                    content = pdf_text
                st.success("✅ PDF loaded!")
        else:
            topic_input = st.text_area(
                "Enter Topic",
                placeholder="e.g., Post Office Act 2023, Prevention of Money Laundering Act, etc.",
                height=100
            )
            topic = topic_input if topic_input else None
            content = topic_input
            st.session_state.topic = topic_input
        
        st.session_state.content = content
        
        # Generate Test button
        if st.button("🚀 Generate MCQs", type="primary", use_container_width=True):
            if content:
                with st.spinner(f"Generating {num_questions} MCQs..."):
                    client = init_groq_client()
                    questions = generate_mcq_questions(
                        client,
                        content,
                        num_questions,
                        topic,
                        language
                    )
                    if questions:
                        st.session_state.questions = questions
                        st.session_state.current_question = 0
                        st.session_state.answers = {}
                        st.session_state.results = {}
                        st.session_state.test_started = True
                        st.success(f"✅ {len(questions)} questions generated!")
                        st.rerun()
                    else:
                        st.error("Failed to generate questions. Please try again.")
            else:
                st.warning("Please provide content (PDF or topic) first.")
        
        # Progress and score in sidebar (during test)
        if st.session_state.test_started and st.session_state.questions:
            st.divider()
            st.subheader("📊 Test Progress")
            answered = len([a for a in st.session_state.answers.values() if a])
            total = len(st.session_state.questions)
            st.progress(answered/total if total>0 else 0)
            st.write(f"Answered: {answered}/{total}")
            if answered == total and st.session_state.results:
                correct = sum(1 for r in st.session_state.results.values() if r.get('is_correct', False))
                st.metric("🎯 Score", f"{correct}/{total}")
    
    # ---------- TAB 1: READING MATERIAL ----------
    with tab1:
        st.subheader("📖 Study Material")
        if st.session_state.pdf_text:
            st.markdown("**Extracted from PDF:**")
            with st.expander("Show/Hide Text", expanded=True):
                st.markdown(f'<div class="content-box">{st.session_state.pdf_text}</div>', unsafe_allow_html=True)
        elif st.session_state.topic:
            st.markdown("**Your Topic:**")
            st.info(st.session_state.topic)
        else:
            st.info("👈 Upload a PDF or enter a topic in the sidebar to see it here.")
    
    # ---------- TAB 2: GENERATE TEST (Quick MCQ generation and take) ----------
    with tab2:
        if st.session_state.questions:
            st.subheader(f"Generated MCQs ({len(st.session_state.questions)} questions)")
            # Show all questions and answers in an expandable way
            for i, q in enumerate(st.session_state.questions):
                with st.expander(f"Q{i+1}: {q['question'][:100]}..."):
                    st.write(q['question'])
                    for opt in q['options']:
                        st.write(f"- {opt}")
                    st.write(f"**Correct Answer:** {q['correct_answer']}")
                    st.write(f"**Explanation:** {q['explanation']}")
        else:
            st.info("No MCQs generated yet. Use the sidebar to upload content and click 'Generate MCQs'.")
    
    # ---------- TAB 3: MOCK TEST ----------
    with tab3:
        if not st.session_state.test_started or not st.session_state.questions:
            st.info("No test available. Generate MCQs first using the sidebar.")
        else:
            questions = st.session_state.questions
            current_idx = st.session_state.current_question
            
            if current_idx < len(questions):
                q = questions[current_idx]
                
                # Question card
                st.markdown(f"""
                <div class="question-card">
                    <h3>📝 Question {current_idx + 1} of {len(questions)}</h3>
                    <p style="font-size:1.1rem; margin-top:10px;">{q['question']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Options
                options = q['options']
                user_answer = st.session_state.answers.get(current_idx, "")
                answer = st.radio(
                    "Select your answer:",
                    options,
                    index=options.index(user_answer) if user_answer in options else 0,
                    key=f"q_{current_idx}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Submit Answer", use_container_width=True):
                        if answer:
                            st.session_state.answers[current_idx] = answer
                            client = init_groq_client()
                            with st.spinner("Evaluating..."):
                                evaluation = evaluate_answer(
                                    client,
                                    q['question'],
                                    answer,
                                    q['correct_answer'],
                                    q['explanation']
                                )
                                st.session_state.results[current_idx] = evaluation
                            st.rerun()
                with col2:
                    if current_idx < len(questions) - 1:
                        if st.button("⏭️ Next Question", use_container_width=True):
                            st.session_state.current_question += 1
                            st.rerun()
                    else:
                        if st.button("🏆 Finish Test", use_container_width=True):
                            st.session_state.current_question = len(questions)
                            st.rerun()
                
                # Feedback for current question
                if current_idx in st.session_state.results:
                    res = st.session_state.results[current_idx]
                    if res['is_correct']:
                        st.success(f"✅ Correct! {res['feedback']}")
                    else:
                        st.error(f"❌ Incorrect! {res['feedback']}")
                        with st.expander("📖 Show Correct Answer & Explanation"):
                            st.info(f"**Correct Answer:** {q['correct_answer']}\n\n**Explanation:** {q['explanation']}")
            
            else:
                # Test completed
                st.balloons()
                st.success("🎉 Test Completed!")
                st.subheader("📝 Detailed Results")
                correct_count = 0
                for i, q in enumerate(questions):
                    with st.expander(f"Q{i+1}: {q['question'][:100]}..."):
                        st.write(f"**Your answer:** {st.session_state.answers.get(i, 'Not answered')}")
                        st.write(f"**Correct answer:** {q['correct_answer']}")
                        if i in st.session_state.results:
                            res = st.session_state.results[i]
                            if res['is_correct']:
                                st.success(res['feedback'])
                                correct_count += 1
                            else:
                                st.error(res['feedback'])
                        st.write(f"**Explanation:** {q['explanation']}")
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📝 Total Questions", len(questions))
                with col2:
                    st.metric("✅ Correct", correct_count)
                with col3:
                    st.metric("📊 Score", f"{(correct_count/len(questions)*100):.1f}%")
                
                if st.button("🔄 Start New Test", type="primary", use_container_width=True):
                    st.session_state.test_started = False
                    st.session_state.questions = []
                    st.rerun()

if __name__ == "__main__":
    main()
