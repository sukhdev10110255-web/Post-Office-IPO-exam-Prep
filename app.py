import streamlit as st
import os
import PyPDF2
from groq import Groq
import json
import re
from typing import List, Dict

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="📚 Exam Warrior | AI Test Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== LIGHT THEME CSS ==========
st.markdown("""
<style>
    /* Main container - Light background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    }
    
    /* Headers styling */
    h1, h2, h3 {
        font-family: 'Poppins', 'Segoe UI', sans-serif;
        color: #1e3c72;
    }
    
    h1 {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        border-left: 5px solid #1e3c72;
        padding-left: 20px;
    }
    
    /* Sidebar styling - Light */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        border-right: 1px solid #e0e0e0;
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        font-weight: 600;
        font-size: 16px;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30,60,114,0.3);
        background: linear-gradient(90deg, #2a5298, #1e3c72);
    }
    
    /* Card styling */
    .question-card {
        background: white;
        border-left: 4px solid #1e3c72;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #1e3c72;
    }
    
    /* Radio buttons */
    .stRadio label {
        font-size: 15px;
        padding: 8px;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .stRadio label:hover {
        background: rgba(30,60,114,0.05);
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 8px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(30,60,114,0.05);
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Info boxes */
    .info-box {
        background: #e8f0fe;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    
    /* Sidebar text */
    .sidebar-text {
        color: #1e3c72;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ========== GROQ CLIENT INITIALIZATION ==========
@st.cache_resource
def init_groq_client():
    """Initialize Groq client with proper error handling"""
    # Try environment variable first (Render, etc.)
    api_key = os.getenv("GROQ_API_KEY")
    
    # If not found, try Streamlit secrets
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
        - **Local:** Create `.env` file with `GROQ_API_KEY=your-key`
        
        Get your free API key: https://console.groq.com
        """)
        st.stop()
    
    return Groq(api_key=api_key)

# ========== PDF TEXT EXTRACTION ==========
def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF"""
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

# ========== MCQ QUESTION GENERATION ==========
def generate_mcq_questions(client: Groq, content: str, num_questions: int, topic: str = None) -> List[Dict]:
    """Generate MCQs using Groq API - Updated with working model"""
    
    # Using llama3-70b which is currently available (updated from deprecated mixtral)
    model_name = "llama3-70b-8192"  # New working model
    
    prompt = f"""
    Generate {num_questions} multiple-choice questions.
    
    {"Topic: " + topic if topic else "Based on this content:"}
    
    Content:
    {content[:7000]}
    
    Return ONLY valid JSON in this exact format:
    {{
        "questions": [
            {{
                "question": "Question text?",
                "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                "correct_answer": "A. Option 1",
                "explanation": "Detailed explanation"
            }}
        ]
    }}
    
    Rules:
    - Each question must have exactly 4 options
    - Make questions challenging but fair
    - Provide clear explanations
    - Return ONLY valid JSON
    """
    
    try:
        completion = client.chat.completions.create(
            model=model_name,  # Updated model
            messages=[
                {"role": "system", "content": "You are an expert exam creator. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
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
def evaluate_answer(client: Groq, question: str, user_answer: str, correct_answer: str, explanation: str) -> Dict:
    """Evaluate user's answer"""
    
    model_name = "llama3-70b-8192"  # Updated model
    
    prompt = f"""
    Evaluate this answer:
    
    Question: {question}
    User's Answer: {user_answer}
    Correct Answer: {correct_answer}
    
    Return ONLY JSON:
    {{
        "is_correct": true/false,
        "feedback": "Short feedback (max 50 words)"
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a strict evaluator. Return only valid JSON."},
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

# ========== MAIN APP ==========
def main():
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1>📚 EXAM WARRIOR</h1>
        <p style="color: #1e3c72; font-size: 1.1rem;">
            AI-Powered MCQ Test Generator for Exam Preparation
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Session state initialization
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'results' not in st.session_state:
        st.session_state.results = {}
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ **Configuration**")
        st.markdown("---")
        
        # Input method
        input_method = st.radio(
            "**Select Input Method:**",
            ["📄 Upload PDF", "✏️ Enter Topic"],
            horizontal=False
        )
        
        num_questions = st.slider("**Number of Questions:**", 3, 20, 10)
        
        st.markdown("---")
        
        # Content input
        if "PDF" in input_method:
            uploaded_file = st.file_uploader("**Upload PDF File**", type="pdf")
            content = None
            if uploaded_file:
                with st.spinner("Extracting text from PDF..."):
                    content = extract_text_from_pdf(uploaded_file)
                st.success("✅ PDF loaded successfully!")
        else:
            topic = st.text_area(
                "**Enter Topic:**",
                placeholder="e.g., Indian Polity, Machine Learning, World History...",
                height=100
            )
            content = topic if topic else None
        
        st.markdown("---")
        
        # Generate button
        if st.button("🚀 **Generate Test**", use_container_width=True):
            if content:
                with st.spinner(f"Generating {num_questions} questions..."):
                    client = init_groq_client()
                    questions = generate_mcq_questions(
                        client, content, num_questions,
                        topic if "Topic" in input_method else None
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
                st.warning("⚠️ Please provide PDF or topic first!")
        
        # Progress tracker
        if st.session_state.test_started and st.session_state.questions:
            st.markdown("---")
            st.markdown("### 📊 **Progress**")
            answered = len([a for a in st.session_state.answers.values() if a])
            total = len(st.session_state.questions)
            st.progress(answered/total if total > 0 else 0)
            st.write(f"Answered: {answered}/{total}")
            
            if answered == total and st.session_state.results:
                correct = sum(1 for r in st.session_state.results.values() if r.get('is_correct', False))
                st.markdown("---")
                st.markdown("### 🎯 **Score**")
                st.metric("Correct Answers", f"{correct}/{total}")
                st.markdown(f"**Success Rate:** {(correct/total*100):.1f}%")
    
    # Main content area
    if st.session_state.test_started and st.session_state.questions:
        questions = st.session_state.questions
        current_idx = st.session_state.current_question
        
        if current_idx < len(questions):
            q = questions[current_idx]
            
            # Question card
            st.markdown(f"""
            <div class="question-card">
                <h3 style="color: #1e3c72;">📝 Question {current_idx + 1} / {len(questions)}</h3>
                <h2 style="font-size: 1.3rem;">{q['question']}</h2>
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
                        client = init_groq_client()
                        with st.spinner("Evaluating..."):
                            evaluation = evaluate_answer(
                                client, q['question'], answer,
                                q['correct_answer'], q['explanation']
                            )
                            st.session_state.results[current_idx] = evaluation
                        st.rerun()
            
            with col2:
                if current_idx < len(questions) - 1:
                    if st.button("⏭️ Next Question", use_container_width=True):
                        st.session_state.current_question += 1
                        st.rerun()
                else:
                    if st.button("🏆 Show Results", use_container_width=True):
                        st.session_state.current_question = len(questions)
                        st.rerun()
            
            # Feedback
            if current_idx in st.session_state.results:
                result = st.session_state.results[current_idx]
                if result['is_correct']:
                    st.success(f"✅ Correct! {result['feedback']}")
                else:
                    st.error(f"❌ Incorrect! {result['feedback']}")
                    with st.expander("📖 View Correct Answer"):
                        st.info(f"**Correct answer:** {q['correct_answer']}\n\n**Explanation:** {q['explanation']}")
        
        else:
            # Results screen
            st.balloons()
            st.markdown("""
            <div style="text-align: center; padding: 30px;">
                <h1 style="color: #1e3c72;">🎉 Test Completed!</h1>
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed results
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
            
            # Score summary
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📝 Total Questions", len(questions))
            with col2:
                st.metric("✅ Correct", correct_count)
            with col3:
                st.metric("📊 Success Rate", f"{(correct_count/len(questions)*100):.1f}%")
            
            if st.button("🔄 Start New Test", type="primary", use_container_width=True):
                for key in ['questions', 'current_question', 'answers', 'results', 'test_started']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    else:
        # Welcome screen
        st.markdown("""
        <div class="info-box">
            <h2 style="color: #1e3c72;">⚡ Ready for Test?</h2>
            <p>Upload your PDF or enter a topic in the sidebar<br>
            Then click Generate Test to start!</p>
            <hr>
            <p><strong>Features:</strong> 📄 PDF Upload | ✏️ Topic Input | ⚡ Instant Evaluation | 📊 Score Tracking</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
