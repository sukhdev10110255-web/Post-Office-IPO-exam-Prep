import streamlit as st
import os
import PyPDF2
import json
import re
from typing import List, Dict, Optional
from cerebras.cloud.sdk import Cerebras

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
    .stApp { background: #f8fafc; }
    h1, h2, h3 { color: #1e3c72; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e2e8f0; }
    .stButton button { background: #1e3c72; color: white; font-weight: 600; border-radius: 8px; transition: all 0.3s ease; }
    .stButton button:hover { background: #2a5298; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(30,60,114,0.2); }
    .question-card { background: white; border-left: 4px solid #1e3c72; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .stProgress > div > div { background: #1e3c72; }
    [data-testid="stMetricValue"] { color: #1e3c72; font-size: 2rem; font-weight: bold; }
    .content-box { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; max-height: 500px; overflow-y: auto; }
    .stAlert { border-left: 4px solid #1e3c72; }
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ========== CEREBRAS CLIENT ==========
@st.cache_resource
def init_cerebras_client():
    """Initialize Cerebras client with API key from environment or secrets"""
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("CEREBRAS_API_KEY")
        except:
            pass
    
    if not api_key:
        st.error("""
        ❌ **CEREBRAS_API_KEY Not Found!**
        
        Please add your Cerebras API key:
        - **Render:** Environment variable `CEREBRAS_API_KEY`
        - **Streamlit Cloud:** Add to secrets.toml
        
        Get your free key at [cloud.cerebras.ai](https://cloud.cerebras.ai)
        (Free tier: 1M tokens/day! No credit card required)
        """)
        st.stop()
    
    return Cerebras(api_key=api_key)

# ========== PDF TEXT EXTRACTION ==========
def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF file"""
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

# ========== GENERATE NOTES (BILINGUAL) ==========
def generate_notes(client: Cerebras, content: str, topic: Optional[str] = None) -> str:
    """Generate structured study notes in Hindi and English"""
    
    prompt = f"""
    You are an expert teacher for Inspector Posts LDCE exam. Create comprehensive study notes in BOTH Hindi and English.
    
    Topic: {topic if topic else "Based on the provided content"}
    
    Content:
    {content[:150000]}  # Cerebras can handle 150K tokens easily!
    
    Format each section as:
    
    ## [Topic Name in English]
    ### English Explanation
    [Detailed explanation in English]
    
    ### हिंदी व्याख्या (Hindi Explanation)
    [Detailed explanation in Hindi]
    
    Cover all key concepts, important sections, rules, and acts mentioned.
    Make it easy to understand and exam-focused.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama3.3-70b",  # Best model for exam prep
            messages=[
                {"role": "system", "content": "You are an expert exam preparation tutor. Create detailed, accurate notes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=8000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error generating notes: {str(e)}"

# ========== MCQ GENERATION ==========
def generate_mcq_questions(
    client: Cerebras,
    content: str,
    num_questions: int,
    topic: Optional[str] = None,
    language: str = "bilingual"
) -> List[Dict]:
    """Generate multiple choice questions based on content"""
    
    lang_instruction = {
        "english": "Generate all questions and options ONLY in English.",
        "hindi": "Generate all questions and options ONLY in Hindi. Use Devanagari script.",
        "bilingual": "Generate each question in BOTH English and Hindi. Format: English version first, then Hindi version below it."
    }.get(language, "Generate in English.")
    
    prompt = f"""
    You are an expert examiner for Inspector Posts LDCE exam.
    
    {lang_instruction}
    
    Based on the following content, generate {num_questions} high-quality multiple-choice questions.
    
    {"Topic: " + topic if topic else ""}
    
    Content:
    {content[:100000]}
    
    Return ONLY valid JSON in this exact format:
    {{
        "questions": [
            {{
                "question": "Question text (bilingual if requested)",
                "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                "correct_answer": "A. Option 1",
                "explanation": "Detailed explanation in English of why this is correct"
            }}
        ]
    }}
    
    Requirements:
    - Each question must have exactly 4 options
    - Options should be challenging but fair
    - Questions should test understanding, not just memorization
    - Provide clear, educational explanations
    - Return ONLY valid JSON, no other text
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama3.3-70b",
            messages=[
                {"role": "system", "content": "You are an expert MCQ creator. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000
        )
        
        response_text = completion.choices[0].message.content
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            questions_data = json.loads(json_match.group())
            return questions_data.get("questions", [])
        return []
        
    except Exception as e:
        st.error(f"🔥 Generation Error: {str(e)}")
        return []

# ========== ANSWER EVALUATION ==========
def evaluate_answer(client: Cerebras, question: str, user_answer: str, correct_answer: str, explanation: str) -> Dict:
    """Evaluate user's answer and provide feedback"""
    
    prompt = f"""
    Evaluate this answer strictly:
    
    Question: {question}
    User's Answer: {user_answer}
    Correct Answer: {correct_answer}
    Expected Explanation: {explanation}
    
    Return ONLY JSON in this format:
    {{
        "is_correct": true/false,
        "feedback": "Short, constructive feedback (max 60 words)"
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama3.1-8b-instant",  # Faster for evaluation
            messages=[
                {"role": "system", "content": "You are a strict evaluator. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        response_text = completion.choices[0].message.content
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"is_correct": False, "feedback": "Evaluation failed"}
        
    except Exception as e:
        return {"is_correct": False, "feedback": f"Error: {str(e)}"}

# ========== SESSION STATE INITIALIZATION ==========
def init_session():
    """Initialize all session state variables"""
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
        'num_questions': 10,
        'notes': None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ========== MAIN APP ==========
def main():
    init_session()
    
    # Header
    st.title("📚 LDCE Inspector Posts Exam Preparation")
    st.markdown("### 🚀 AI-Powered Study Assistant | Powered by Cerebras (1M Tokens/DAY Free!)")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Language selection
        language = st.selectbox(
            "📖 Question Language",
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
        num_questions = st.slider("📝 Number of Questions", 3, 20, 10)
        st.session_state.num_questions = num_questions
        
        st.divider()
        
        # Input method
        input_method = st.radio(
            "📂 Input Method",
            ["📄 Upload PDF", "✏️ Enter Topic"],
            horizontal=True
        )
        
        content = None
        topic = None
        
        if input_method == "📄 Upload PDF":
            uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
            if uploaded_file:
                with st.spinner("📖 Extracting text from PDF..."):
                    pdf_text = extract_text_from_pdf(uploaded_file)
                    st.session_state.pdf_text = pdf_text
                    content = pdf_text
                st.success(f"✅ PDF loaded! ({len(content)} characters)")
                if len(content) > 100000:
                    st.info("ℹ️ Large PDF detected. Cerebras can handle it easily!")
        else:
            topic_input = st.text_area(
                "📝 Enter Topic",
                placeholder="e.g., Post Office Act 2023, Prevention of Money Laundering Act, Constitution of India...",
                height=100
            )
            topic = topic_input if topic_input else None
            content = topic_input
            st.session_state.topic = topic_input
        
        st.session_state.content = content
        
        st.divider()
        
        # Generate Notes button
        if st.button("📝 Generate Notes", type="primary", use_container_width=True):
            if content:
                with st.spinner("📚 Creating comprehensive notes in Hindi & English..."):
                    client = init_cerebras_client()
                    notes = generate_notes(client, content, topic)
                    st.session_state.notes = notes
                    st.success("✅ Notes generated successfully!")
                    st.rerun()
            else:
                st.warning("⚠️ Please provide PDF or topic first.")
        
        # Generate MCQs button
        if st.button("🚀 Generate MCQs", use_container_width=True):
            if content:
                with st.spinner(f"🎯 Generating {num_questions} MCQs..."):
                    client = init_cerebras_client()
                    questions = generate_mcq_questions(
                        client, content, num_questions, topic, language
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
                        st.error("❌ Failed to generate questions. Please try again.")
            else:
                st.warning("⚠️ Please provide PDF or topic first.")
        
        # Progress tracker during test
        if st.session_state.test_started and st.session_state.questions:
            st.divider()
            st.subheader("📊 Test Progress")
            answered = len([a for a in st.session_state.answers.values() if a])
            total = len(st.session_state.questions)
            st.progress(answered/total if total > 0 else 0)
            st.write(f"Answered: {answered}/{total}")
            
            if answered == total and st.session_state.results:
                correct = sum(1 for r in st.session_state.results.values() if r.get('is_correct', False))
                st.metric("🎯 Score", f"{correct}/{total}")
                st.write(f"**Success Rate:** {(correct/total*100):.1f}%")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Reading Material", "📝 Study Notes", "✍️ MCQ Bank", "📝 Mock Test"])
    
    # Tab 1: Reading Material
    with tab1:
        st.subheader("📖 Your Study Material")
        if st.session_state.pdf_text:
            st.markdown(f'<div class="content-box">{st.session_state.pdf_text}</div>', unsafe_allow_html=True)
        elif st.session_state.topic:
            st.info(f"**Topic:** {st.session_state.topic}")
        else:
            st.info("👈 **Get Started:** Upload a PDF or enter a topic in the sidebar")
            st.markdown("""
            ### 📚 Suggested Topics for LDCE Exam:
            - Post Office Act 2023
            - Prevention of Money Laundering Act, 2002
            - Government Savings Promotion Rules, 2018
            - Consumer Protection Act, 2019
            - Constitution of India (Fundamental Rights, DPSP)
            - CCS (Pension) Rules, 2021
            - RTI Act, 2005
            - Prevention of Corruption Act, 1988
            """)
    
    # Tab 2: Study Notes
    with tab2:
        st.subheader("📝 Generated Study Notes")
        if st.session_state.notes:
            st.markdown(st.session_state.notes)
        else:
            st.info("💡 Click **'Generate Notes'** in the sidebar to create bilingual study notes.")
            st.markdown("""
            ### What you'll get:
            - 📖 **Detailed explanations** in both English and Hindi
            - 📋 **Key concepts** from the syllabus
            - 🎯 **Exam-focused content** for LDCE Inspector Posts
            """)
    
    # Tab 3: MCQ Bank
    with tab3:
        st.subheader("✍️ Generated MCQ Bank")
        if st.session_state.questions:
            st.info(f"📊 Total {len(st.session_state.questions)} questions available")
            for i, q in enumerate(st.session_state.questions):
                with st.expander(f"Q{i+1}: {q['question'][:150]}..."):
                    st.markdown(f"**Question:** {q['question']}")
                    st.markdown("**Options:**")
                    for opt in q['options']:
                        st.write(f"- {opt}")
                    st.markdown(f"**✅ Correct Answer:** {q['correct_answer']}")
                    st.markdown(f"**📖 Explanation:** {q['explanation']}")
        else:
            st.info("💡 Click **'Generate MCQs'** in the sidebar to create practice questions.")
    
    # Tab 4: Mock Test
    with tab4:
        if not st.session_state.test_started or not st.session_state.questions:
            st.info("🎯 No active test. Generate MCQs first to start practicing!")
        else:
            questions = st.session_state.questions
            current_idx = st.session_state.current_question
            
            if current_idx < len(questions):
                q = questions[current_idx]
                
                # Question display
                st.markdown(f"""
                <div class="question-card">
                    <h3>📝 Question {current_idx + 1} of {len(questions)}</h3>
                    <p style="font-size: 1.1rem; margin-top: 10px;">{q['question']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Options
                options = q['options']
                user_answer = st.session_state.answers.get(current_idx, "")
                
                answer = st.radio(
                    "**Select your answer:**",
                    options,
                    index=options.index(user_answer) if user_answer in options else 0,
                    key=f"q_{current_idx}"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Submit Answer", use_container_width=True):
                        if answer:
                            st.session_state.answers[current_idx] = answer
                            client = init_cerebras_client()
                            with st.spinner("⚡ Evaluating..."):
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
                    result = st.session_state.results[current_idx]
                    if result['is_correct']:
                        st.success(f"✅ **Correct!** {result['feedback']}")
                    else:
                        st.error(f"❌ **Incorrect!** {result['feedback']}")
                        with st.expander("📖 View Correct Answer & Explanation"):
                            st.info(f"**Correct Answer:** {q['correct_answer']}\n\n**Explanation:** {q['explanation']}")
            
            else:
                # Test completed
                st.balloons()
                st.success("🎉 **Test Completed!** 🎉")
                
                # Calculate score
                correct_count = 0
                for i, q in enumerate(questions):
                    with st.expander(f"Question {i+1}: {q['question'][:100]}..."):
                        st.write(f"**Your answer:** {st.session_state.answers.get(i, 'Not answered')}")
                        st.write(f"**Correct answer:** {q['correct_answer']}")
                        if i in st.session_state.results:
                            result = st.session_state.results[i]
                            if result['is_correct']:
                                st.success(result['feedback'])
                                correct_count += 1
                            else:
                                st.error(result['feedback'])
                        st.write(f"**Explanation:** {q['explanation']}")
                
                # Score su
