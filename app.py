import streamlit as st
import os
import PyPDF2
from groq import Groq
import json
import re
from typing import List, Dict
import time

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="⚡ EXAM WARRIOR | AI Test Generator",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS FOR AGGRESSIVE DARK THEME ==========
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    
    /* Headers with aggressive styling */
    h1, h2, h3 {
        font-family: 'Impact', 'Arial Black', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    h1 {
        background: linear-gradient(135deg, #ff0000, #ff6600);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(255,0,0,0.5);
        font-size: 3.5rem;
        border-left: 5px solid #ff0000;
        padding-left: 20px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a2a 100%);
        border-right: 2px solid #ff3300;
    }
    
    /* Button styling - AGGRESSIVE */
    .stButton button {
        background: linear-gradient(90deg, #ff0000, #ff3300);
        color: white;
        font-weight: bold;
        font-size: 18px;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 15px rgba(255,0,0,0.5);
    }
    
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(255,0,0,0.8);
        background: linear-gradient(90deg, #ff3300, #ff0000);
    }
    
    /* Cards styling */
    .question-card {
        background: rgba(0,0,0,0.7);
        border-left: 4px solid #ff3300;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.5);
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, #ff0000, #ff6600);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff3300;
    }
    
    /* Radio buttons styling */
    .stRadio label {
        font-size: 16px;
        font-weight: 500;
        padding: 10px;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .stRadio label:hover {
        background: rgba(255,51,0,0.1);
    }
    
    /* Success/Error messages */
    .stAlert {
        border-left: 4px solid #ff3300;
        border-radius: 8px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255,51,0,0.1);
        border-radius: 8px;
        font-weight: bold;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a2a;
    }
    ::-webkit-scrollbar-thumb {
        background: #ff3300;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #ff0000;
    }
    
    /* Animated background effect */
    @keyframes pulse {
        0% { opacity: 0.3; }
        100% { opacity: 0.6; }
    }
</style>
""", unsafe_allow_html=True)

# ========== GROQ CLIENT INITIALIZATION (FIXED) ==========
@st.cache_resource
def init_groq_client():
    """Initialize Groq client with proper error handling"""
    # Try environment variable first (Render, Heroku, etc.)
    api_key = os.getenv("GROQ_API_KEY")
    
    # If not found, try Streamlit secrets (Streamlit Cloud)
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY")
        except:
            pass
    
    if not api_key:
        st.error("""
        ⚔️ **GROQ_API_KEY NOT FOUND!** ⚔️
        
        ### 🔥 To fix this:
        
        1. **Get your API key:** [console.groq.com](https://console.groq.com)
        2. **Add it to Render:**
           - Go to your service → Environment tab
           - Add variable: `GROQ_API_KEY` = `your-key-here`
        
        3. **Or add to Streamlit Cloud:**
           - Settings → Secrets → Add `GROQ_API_KEY`
        
        ### 💪 Don't have a key? 
        - Sign up for free at Groq.com
        - Get 30+ requests/minute free tier
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
    """Generate MCQs using Groq API"""
    
    prompt = f"""
    You are a ruthless exam creator. Generate {num_questions} high-quality multiple-choice questions.
    
    {"Topic: " + topic if topic else "Based on this content:"}
    
    Content:
    {content[:7000]}
    
    IMPORTANT: Return ONLY valid JSON in this exact format:
    {{
        "questions": [
            {{
                "question": "Question text here?",
                "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                "correct_answer": "A. Option 1",
                "explanation": "Detailed explanation why this is correct"
            }}
        ]
    }}
    
    Rules:
    - Each question must have exactly 4 options
    - Make options challenging but fair
    - Test deep understanding, not just memorization
    - Provide clear, educational explanations
    - Return ONLY valid JSON, no other text
    """
    
    try:
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert exam creator. Generate challenging MCQs. Return only valid JSON."},
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
    """Evaluate user's answer with Groq"""
    
    prompt = f"""
    Evaluate this answer STRICTLY:
    
    Question: {question}
    User's Answer: {user_answer}
    Correct Answer: {correct_answer}
    
    Return ONLY JSON:
    {{
        "is_correct": true/false,
        "feedback": "Short, powerful feedback (max 50 words)"
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
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
    # Animated header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1>⚔️ EXAM WARRIOR ⚔️</h1>
        <p style="color: #ff6600; font-size: 1.2rem; letter-spacing: 2px;">
            🔥 AI-POWERED MCQ COMBAT TRAINING 🔥
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
    
    # Sidebar - Weapon Config
    with st.sidebar:
        st.markdown("### ⚔️ **BATTLE CONFIG** ⚔️")
        st.markdown("---")
        
        # Input method
        input_method = st.radio(
            "**SELECT WEAPON:**",
            ["📄 PDF ATTACK", "🎯 TOPIC STRIKE"],
            horizontal=False
        )
        
        num_questions = st.slider("**QUESTIONS COUNT:**", 3, 20, 10)
        
        st.markdown("---")
        
        # Content input
        if "PDF" in input_method:
            uploaded_file = st.file_uploader("**DEPLOY PDF**", type="pdf")
            content = None
            if uploaded_file:
                with st.spinner("🔍 Extracting intel..."):
                    content = extract_text_from_pdf(uploaded_file)
                st.success("✅ PDF loaded!")
        else:
            topic = st.text_area(
                "**TARGET TOPIC:**",
                placeholder="e.g., Indian Polity, Machine Learning, World History...",
                height=100
            )
            content = topic if topic else None
        
        st.markdown("---")
        
        # Generate button
        if st.button("💥 **GENERATE TEST** 💥", use_container_width=True):
            if content:
                with st.spinner("⚡ Generating battle questions..."):
                    client = init_groq_client()
                    questions = generate_mcq_questions(
                        client, content, num_questions,
                        topic if "TOPIC" in input_method else None
                    )
                    
                    if questions:
                        st.session_state.questions = questions
                        st.session_state.current_question = 0
                        st.session_state.answers = {}
                        st.session_state.results = {}
                        st.session_state.test_started = True
                        st.success(f"✅ {len(questions)} questions ready for battle!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate! Check API key or content.")
            else:
                st.warning("⚠️ Deploy PDF or target topic first!")
        
        # Progress tracker
        if st.session_state.test_started and st.session_state.questions:
            st.markdown("---")
            st.markdown("### 📊 **BATTLE PROGRESS**")
            answered = len([a for a in st.session_state.answers.values() if a])
            total = len(st.session_state.questions)
            st.progress(answered/total if total > 0 else 0)
            st.metric("**ENEMIES DEFEATED**", f"{answered}/{total}")
            
            if answered == total and st.session_state.results:
                correct = sum(1 for r in st.session_state.results.values() if r.get('is_correct', False))
                st.markdown("---")
                st.markdown("### 🏆 **FINAL SCORE**")
                st.metric("**VICTORY RATE**", f"{(correct/total*100):.1f}%")
                st.markdown(f"**Correct:** {correct} / {total}")
    
    # Main battle arena
    if st.session_state.test_started and st.session_state.questions:
        questions = st.session_state.questions
        current_idx = st.session_state.current_question
        
        if current_idx < len(questions):
            q = questions[current_idx]
            
            # Question card
            st.markdown(f"""
            <div class="question-card">
                <h3 style="color: #ff6600;">⚔️ QUESTION {current_idx + 1} / {len(questions)}</h3>
                <h2 style="font-size: 1.5rem;">{q['question']}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Options
            options = q['options']
            user_answer = st.session_state.answers.get(current_idx, "")
            
            answer = st.radio(
                "**SELECT YOUR STRIKE:**",
                options,
                index=options.index(user_answer) if user_answer in options else 0,
                key=f"q_{current_idx}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎯 **SUBMIT ANSWER**", use_container_width=True):
                    if answer:
                        st.session_state.answers[current_idx] = answer
                        client = init_groq_client()
                        with st.spinner("⚡ Evaluating..."):
                            evaluation = evaluate_answer(
                                client, q['question'], answer,
                                q['correct_answer'], q['explanation']
                            )
                            st.session_state.results[current_idx] = evaluation
                        st.rerun()
            
            with col2:
                if current_idx < len(questions) - 1:
                    if st.button("⏭️ **NEXT BATTLE**", use_container_width=True):
                        st.session_state.current_question += 1
                        st.rerun()
                else:
                    if st.button("🏆 **SHOW RESULTS**", use_container_width=True):
                        st.session_state.current_question = len(questions)
                        st.rerun()
            
            # Feedback
            if current_idx in st.session_state.results:
                result = st.session_state.results[current_idx]
                if result['is_correct']:
                    st.success(f"✅ **VICTORY!** {result['feedback']}")
                else:
                    st.error(f"❌ **DEFEATED!** {result['feedback']}")
                    with st.expander("📖 **REVIEW STRATEGY**"):
                        st.info(f"**Correct Answer:** {q['correct_answer']}\n\n**Explanation:** {q['explanation']}")
        
        else:
            # Results screen
            st.balloons()
            st.markdown("""
            <div style="text-align: center; padding: 40px;">
                <h1 style="font-size: 3rem;">🏆 BATTLE COMPLETE 🏆</h1>
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed results
            correct_count = 0
            for i, q in enumerate(questions):
                with st.expander(f"⚔️ Question {i+1}: {q['question'][:100]}..."):
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
                st.metric("⚔️ TOTAL BATTLES", len(questions))
            with col2:
                st.metric("✅ VICTORIES", correct_count)
            with col3:
                st.metric("🔥 SUCCESS RATE", f"{(correct_count/len(questions)*100):.1f}%")
            
            if st.button("🔄 **START NEW WAR**", type="primary", use_container_width=True):
                for key in ['questions', 'current_question', 'answers', 'results', 'test_started']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    else:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <h2 style="color: #ff6600;">⚡ READY FOR BATTLE? ⚡</h2>
            <p style="font-size: 1.2rem; margin: 20px 0;">
                Deploy your PDF or target a topic in the sidebar<br>
                Then launch the test generator!
            </p>
            <div style="background: rgba(255,51,0,0.1); padding: 20px; border-radius: 12px; margin-top: 30px;">
                <p>🔥 <strong>Features:</strong> 🔥</p>
                <p>📄 PDF Combat | 🎯 Topic Warfare | ⚡ Instant Evaluation | 🏆 Score Tracking</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
