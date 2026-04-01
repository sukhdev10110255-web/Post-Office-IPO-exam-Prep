import streamlit as st
import os
import PyPDF2
from groq import Groq
import json
import re
from typing import List, Dict, Any
import time

# Initialize Groq client
@st.cache_resource
def init_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("Please set your GROQ_API_KEY in secrets or environment variables")
        st.stop()
    return Groq(api_key=api_key)

# Extract text from PDF
def extract_text_from_pdf(pdf_file) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

# Generate MCQ questions using Groq
def generate_mcq_questions(client: Groq, content: str, num_questions: int, topic: str = None) -> List[Dict]:
    prompt = f"""
    Based on the following content, generate {num_questions} multiple-choice questions (MCQs).
    
    {"Topic: " + topic if topic else "Content provided below:"}
    
    Content:
    {content[:8000]}  # Limit content to avoid token limits
    
    Please generate questions in the following JSON format:
    {{
        "questions": [
            {{
                "question": "Question text",
                "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                "correct_answer": "A. Option 1",
                "explanation": "Brief explanation of why this is correct"
            }}
        ]
    }}
    
    Make sure:
    1. Questions test understanding, not just memorization
    2. All options are plausible
    3. Each question has exactly 4 options
    4. Return only valid JSON
    """
    
    try:
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert exam question generator. Generate high-quality MCQ questions."},
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
        st.error(f"Error generating questions: {str(e)}")
        return []

# Evaluate user's answer
def evaluate_answer(client: Groq, question: str, user_answer: str, correct_answer: str, explanation: str) -> Dict:
    prompt = f"""
    Question: {question}
    User's Answer: {user_answer}
    Correct Answer: {correct_answer}
    Expected Explanation: {explanation}
    
    Evaluate if the user's answer is correct and provide feedback.
    Return JSON format:
    {{
        "is_correct": true/false,
        "feedback": "Detailed feedback for the user"
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an exam evaluator. Evaluate answers strictly."},
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
        return {"is_correct": False, "feedback": f"Error evaluating: {str(e)}"}

# Main app
def main():
    st.set_page_config(
        page_title="Exam Preparation App",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 AI-Powered Exam Preparation")
    st.markdown("Generate MCQs from PDF or topic and test your knowledge!")
    
    # Initialize session state
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
    if 'mode' not in st.session_state:
        st.session_state.mode = "generate"
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Upload PDF", "Enter Topic"],
            horizontal=True
        )
        
        num_questions = st.slider("Number of questions:", 3, 20, 10)
        
        if input_method == "Upload PDF":
            uploaded_file = st.file_uploader("Upload your PDF", type="pdf")
            content = None
            if uploaded_file:
                with st.spinner("Extracting text from PDF..."):
                    content = extract_text_from_pdf(uploaded_file)
                st.success("PDF uploaded successfully!")
        else:
            topic = st.text_area("Enter topic:", placeholder="e.g., Machine Learning fundamentals, World War II, Python programming...")
            content = topic if topic else None
        
        # Generate button
        if st.button("🚀 Generate Test", type="primary", use_container_width=True):
            if content:
                with st.spinner(f"Generating {num_questions} questions..."):
                    client = init_groq_client()
                    questions = generate_mcq_questions(client, content, num_questions, 
                                                       topic if input_method == "Enter Topic" else None)
                    
                    if questions:
                        st.session_state.questions = questions
                        st.session_state.current_question = 0
                        st.session_state.answers = {}
                        st.session_state.results = {}
                        st.session_state.test_started = True
                        st.session_state.mode = "test"
                        st.success(f"✅ Generated {len(questions)} questions!")
                        st.rerun()
                    else:
                        st.error("Failed to generate questions. Please try again.")
            else:
                st.warning("Please provide content (PDF or topic) first!")
        
        # Progress and stats
        if st.session_state.test_started and st.session_state.questions:
            st.divider()
            st.subheader("📊 Progress")
            answered = len([a for a in st.session_state.answers.values() if a])
            total = len(st.session_state.questions)
            st.progress(answered/total if total > 0 else 0)
            st.write(f"Answered: {answered}/{total}")
            
            # Show results if test completed
            if answered == total and st.session_state.results:
                correct = sum(1 for r in st.session_state.results.values() if r.get('is_correct', False))
                st.subheader("🎯 Score")
                st.metric("Correct Answers", f"{correct}/{total}", 
                         delta=f"{(correct/total*100):.1f}%" if total > 0 else "0%")
    
    # Main content area
    if st.session_state.test_started and st.session_state.questions:
        questions = st.session_state.questions
        current_idx = st.session_state.current_question
        
        if current_idx < len(questions):
            # Display current question
            q = questions[current_idx]
            
            st.subheader(f"Question {current_idx + 1} of {len(questions)}")
            st.markdown(f"### {q['question']}")
            
            # Display options
            options = q['options']
            user_answer = st.session_state.answers.get(current_idx, "")
            
            # Radio buttons for answer selection
            answer = st.radio(
                "Select your answer:",
                options,
                index=options.index(user_answer) if user_answer in options else 0,
                key=f"q_{current_idx}"
            )
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("✅ Submit Answer", use_container_width=True):
                    if answer:
                        st.session_state.answers[current_idx] = answer
                        
                        # Evaluate answer
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
                if st.button("⏭️ Next Question", use_container_width=True, 
                           disabled=current_idx >= len(questions)-1):
                    if current_idx + 1 < len(questions):
                        st.session_state.current_question += 1
                        st.rerun()
            
            with col3:
                if st.button("🏁 Finish Test", use_container_width=True):
                    st.session_state.current_question = len(questions)
                    st.rerun()
            
            # Show feedback if answer submitted
            if current_idx in st.session_state.results:
                result = st.session_state.results[current_idx]
                if result['is_correct']:
                    st.success(f"✅ Correct! {result['feedback']}")
                else:
                    st.error(f"❌ Incorrect! {result['feedback']}")
                    with st.expander("📖 View Correct Answer"):
                        st.info(f"Correct answer: {q['correct_answer']}\n\nExplanation: {q['explanation']}")
        
        else:
            # Test completed - show results
            st.balloons()
            st.success("🎉 Test Completed!")
            
            # Display detailed results
            st.subheader("📝 Detailed Results")
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
            
            # Show summary
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Questions", len(questions))
            with col2:
                st.metric("Correct", correct_count)
            with col3:
                st.metric("Score", f"{(correct_count/len(questions)*100):.1f}%")
            
            # Restart button
            if st.button("🔄 Start New Test", type="primary"):
                for key in ['questions', 'current_question', 'answers', 'results', 'test_started']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    else:
        # Welcome screen
        st.info("👈 Please configure your test in the sidebar and click 'Generate Test'")
        
        # Show example
        with st.expander("📖 How it works"):
            st.markdown("""
            1. **Choose input method:** Upload a PDF textbook/notes or enter a specific topic
            2. **Select number of questions:** Choose how many MCQs you want
            3. **Generate test:** AI creates questions based on your content
            4. **Take the test:** Answer questions and get instant feedback
            5. **Review results:** See detailed explanations and your score
            
            💡 **Tip:** The app uses Groq's high-speed AI models for instant question generation and evaluation!
            """)

if __name__ == "__main__":
    main()
