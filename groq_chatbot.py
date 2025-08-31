import streamlit as st
from groq import Groq

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(page_title="Career Path Chatbot", page_icon="🎓", layout="wide")

# Groq API Setup using secrets.toml
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# ==============================
# PROMPT ENGINEERING
# ==============================
SYSTEM_PROMPT = """
You are a friendly and knowledgeable career counselor.

Rules:
1. Always use the student's **quiz results (preferred stream)** as the starting point for advice.
2. Reply in **two parts**:
   - Part 1: Direct answer to the student's question.
   - Part 2: Additional career guidance tips related to their chosen stream.
3. Stay within scope: only discuss careers, education, learning paths, student growth, or related fields.
   Politely refuse unrelated questions.

Be supportive and student-friendly.
"""

def chat_with_counselor(user_prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",   # ✅ supported Groq model
        messages=[
            {"role": "system", "content": "You are an expert career counselor. Guide the user based on their quiz answers."},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )
    
    return response.choices[0].message.content


def predict_careers():
    # Build a summary of quiz answers
    answers_summary = "\n".join(
        [f"{k}: {v}" for k, v in st.session_state.quiz_answers.items()]
    )
    
    career_prompt = f"""
    Student's chosen stream: {st.session_state.selected_stream}
    Student's quiz answers:
    {answers_summary}

    Suggest the top 3 most suitable careers for this student in their chosen stream.
    Answer as a simple comma-separated list.
    """
    careers = chat_with_counselor(career_prompt)
    return careers

# ==============================
# QUIZ QUESTIONS
# ==============================
quiz = {
    "Science": [
        ("Do you enjoy conducting experiments?", ["Yes", "No", "Sometimes"]),
        ("Would you like to work in a lab or field research?", ["Lab", "Field", "Both"]),
        ("Are you curious about how the human body works?", ["Yes", "No", "Somewhat"]),
        ("Do you enjoy solving physics problems?", ["Yes", "No", "Sometimes"]),
        ("Would you like a career in medicine?", ["Yes", "No", "Maybe"]),
        ("Do you enjoy chemistry experiments?", ["Yes", "No", "Sometimes"]),
        ("Do you like studying about space and universe?", ["Yes", "No", "Maybe"]),
        ("Do you want to invent or innovate in technology?", ["Yes", "No", "Maybe"]),
        ("Do you like environmental studies?", ["Yes", "No", "Maybe"]),
        ("Would you prefer to become a scientist or researcher?", ["Scientist", "Researcher", "Not sure"]),
    ],
    "Mathematics": [
        ("Do you enjoy solving puzzles and logical problems?", ["Yes", "No", "Sometimes"]),
        ("Would you like to work in finance or analytics?", ["Yes", "No", "Maybe"]),
        ("Are you interested in computer algorithms?", ["Yes", "No", "Somewhat"]),
        ("Do you enjoy statistics and probability?", ["Yes", "No", "Sometimes"]),
        ("Do you like abstract thinking?", ["Yes", "No", "Sometimes"]),
        ("Do you want to pursue data science?", ["Yes", "No", "Maybe"]),
        ("Do you like optimization problems?", ["Yes", "No", "Maybe"]),
        ("Do you want to become a mathematician?", ["Yes", "No", "Maybe"]),
        ("Do you like teaching mathematics?", ["Yes", "No", "Maybe"]),
        ("Would you prefer working in academia or industry?", ["Academia", "Industry", "Both"]),
    ],
    "Arts": [
        ("Do you enjoy painting, music, or drama?", ["Yes", "No", "Sometimes"]),
        ("Do you want to pursue literature studies?", ["Yes", "No", "Maybe"]),
        ("Do you like philosophy?", ["Yes", "No", "Somewhat"]),
        ("Are you interested in history and culture?", ["Yes", "No", "Maybe"]),
        ("Do you like designing or creating?", ["Yes", "No", "Sometimes"]),
        ("Do you want to work in media or journalism?", ["Yes", "No", "Maybe"]),
        ("Do you like psychology?", ["Yes", "No", "Somewhat"]),
        ("Would you like a career in filmmaking?", ["Yes", "No", "Maybe"]),
        ("Do you enjoy languages?", ["Yes", "No", "Somewhat"]),
        ("Do you want to become a social scientist?", ["Yes", "No", "Maybe"]),
    ],
    "Commerce": [
        ("Do you enjoy learning about business?", ["Yes", "No", "Somewhat"]),
        ("Would you like to become an entrepreneur?", ["Yes", "No", "Maybe"]),
        ("Are you interested in economics?", ["Yes", "No", "Somewhat"]),
        ("Do you like studying accounts?", ["Yes", "No", "Sometimes"]),
        ("Do you want to work in banking?", ["Yes", "No", "Maybe"]),
        ("Do you want to pursue CA/CS/MBA?", ["CA", "CS", "MBA"]),
        ("Do you like finance?", ["Yes", "No", "Somewhat"]),
        ("Do you want to become a business analyst?", ["Yes", "No", "Maybe"]),
        ("Would you like to work in stock market?", ["Yes", "No", "Maybe"]),
        ("Do you want to work in international business?", ["Yes", "No", "Maybe"]),
    ],
}

# ==============================
# SESSION STATE INIT
# ==============================
if "selected_stream" not in st.session_state:
    st.session_state.selected_stream = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "recommendation" not in st.session_state:
    st.session_state.recommendation = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================
# APP TITLE
# ==============================
st.title("🎓 Career Path Recommendation Chatbot")
st.write("Answer the quiz and then chat with your AI career counselor!")

# ==============================
# STEP 1: STREAM SELECTION
# ==============================
if not st.session_state.selected_stream:
    st.header("🌟 Choose Your Preferred Stream First")
    stream_choice = st.radio("Which stream interests you the most?", list(quiz.keys()), index=None)
    if stream_choice:
        st.session_state.selected_stream = stream_choice
        st.session_state.current_question = 0
        st.session_state.quiz_answers = {}
        st.rerun()

# ==============================
# STEP 2: QUIZ (with back button)
# ==============================
if st.session_state.selected_stream and not st.session_state.quiz_submitted:
    stream = st.session_state.selected_stream
    q_list = quiz[stream]
    idx = st.session_state.current_question
    st.header(f"📝 {stream} Quiz — Question {idx+1} of {len(q_list)}")
    
    question, options = q_list[idx]
    st.session_state.quiz_answers[f"{stream}_{idx}"] = st.radio(question, options, key=f"{stream}_{idx}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️ Back", disabled=idx == 0):
            st.session_state.current_question -= 1
            st.rerun()
    with col2:
        if idx < len(q_list) - 1:
            if st.button("Next ➡️", disabled=f"{stream}_{idx}" not in st.session_state.quiz_answers):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button("✅ Submit Quiz", disabled=f"{stream}_{idx}" not in st.session_state.quiz_answers):
                # ✅ Dynamically predict careers
                careers = predict_careers()
                st.session_state.recommendation = (
                    f"✨ Based on your answers, top career options in {stream}:\n{careers}"
                )
                st.session_state.quiz_submitted = True
                st.rerun()
    with col3:
        if st.button("🔁 Reset Quiz"):
            st.session_state.selected_stream = None
            st.session_state.current_question = 0
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.recommendation = ""
            st.session_state.chat_history = []
            st.rerun()

# ==============================
# STEP 3: Show Recommendation
# ==============================
if st.session_state.quiz_submitted:
    st.success(st.session_state.recommendation)

# ==============================
# STEP 4: FREE CHAT
# ==============================
if st.session_state.quiz_submitted:
    st.header("💬 Chat with Your Career Counselor")
    chat_container = st.container()

    with chat_container:
        for speaker, msg in st.session_state.chat_history:
            if speaker == "You":
                st.markdown(
                    f"""
                    <div style="text-align: right; margin: 5px;">
                        <span style="background-color:#DCF8C6; padding:10px; border-radius:12px; display:inline-block;">
                            {msg}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="text-align: left; margin: 5px;">
                        <span style="background-color:#EDEDED; padding:10px; border-radius:12px; display:inline-block;">
                            {msg}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    user_msg = st.text_input("Type your message:", key="chat_input")
    col1, col2 = st.columns([1, 5])
    with col1:
        send_click = st.button("Send")
    with col2:
        clear_click = st.button("Clear Chat")

    if send_click and user_msg:
        st.session_state.chat_history.append(("You", user_msg))
        bot_reply = chat_with_counselor(user_msg)
        st.session_state.chat_history.append(("Counselor", bot_reply))
        st.rerun()

    if clear_click:
        st.session_state.chat_history = []
        st.rerun()

