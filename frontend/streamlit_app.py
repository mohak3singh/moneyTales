"""
Streamlit Frontend
Interactive web interface for MoneyTales
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="MoneyTales - Financial Education for Kids",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional design
st.markdown("""
<style>
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #f093fb;
        --success-color: #4ade80;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
    }
    
    /* Overall app styling */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
    }
    
    /* Main background */
    .stMainBlockContainer {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 2rem 1rem !important;
    }
    
    .main {
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        letter-spacing: -1px;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 2.5rem !important;
    }
    
    h2 {
        color: #1e293b;
        font-weight: 700;
        margin: 1.5rem 0 0.5rem 0 !important;
        font-size: 2rem !important;
    }
    
    h3 {
        color: #334155;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0 !important;
        font-size: 1.25rem !important;
    }
    
    h4 {
        color: #475569;
        font-weight: 600;
        margin: 0.75rem 0 0.5rem 0 !important;
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.12);
        transform: translateY(-2px);
    }
    
    .card-highlight {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border: 2px solid #667eea;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        font-size: 0.95rem !important;
        height: auto !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Input styling */
    .stSelectbox, .stRadio {
        border-radius: 8px;
    }
    
    .stSelectbox > div > div {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }
    
    /* Metric cards */
    .stMetric {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
    }
    
    .stMetricLabel {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid;
    }
    
    .stSuccess {
        background-color: #f0fdf4 !important;
        border-left-color: #4ade80 !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        border-left-color: #f59e0b !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        border-left-color: #ef4444 !important;
    }
    
    /* Divider */
    hr {
        border: 0;
        border-top: 1px solid #e2e8f0;
        margin: 1.5rem 0 !important;
    }
    
    /* User profile badge */
    .user-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        display: inline-block;
        margin: 0;
    }
    
    /* Quiz container */
    .quiz-container {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin: 0;
        border: 1px solid #e2e8f0;
    }
    
    .question-box {
        background: #f8fafc;
        border-left: 4px solid #667eea;
        padding: 16px;
        margin: 12px 0;
        border-radius: 8px;
    }
    
    .story-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 20px;
        margin: 0 0 16px 0;
        line-height: 1.8;
        font-size: 1.05rem;
        color: #334155;
    }
    
    /* Radio button styling */
    .stRadio > div {
        flex-direction: column;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Remove extra padding */
    .element-container {
        margin: 0;
    }
    
    /* Column spacing */
    .row-widget.stButton {
        margin: 0;
    }
    
    /* Text alignment */
    p {
        margin: 0.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

# Load user credentials from backend on startup
@st.cache_resource
def load_user_credentials():
    """Load registered user credentials from backend"""
    try:
        response = requests.get(f"http://localhost:8000/api/auth/credentials", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("credentials", {})
    except Exception as e:
        print(f"Could not load credentials from backend: {e}")
    return {}

# Session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_age" not in st.session_state:
    st.session_state.user_age = None
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "current_answers" not in st.session_state:
    st.session_state.current_answers = []
if "page" not in st.session_state:
    st.session_state.page = "explore"
if "show_register" not in st.session_state:
    st.session_state.show_register = False
if "available_topics" not in st.session_state:
    st.session_state.available_topics = []

# User credentials mapping (user_id, name, password)
USERS_CREDENTIALS = {
    "alex": {"user_id": "child_001", "name": "Alex", "password": "alex123", "age": 10},
    "sam": {"user_id": "child_002", "name": "Sam", "password": "sam123", "age": 12},
    "jordan": {"user_id": "child_003", "name": "Jordan", "password": "jordan123", "age": 8},
    "casey": {"user_id": "child_004", "name": "Casey", "password": "casey123", "age": 11},
}

# Merge demo credentials with registered credentials
REGISTERED_CREDENTIALS = load_user_credentials()
USERS_CREDENTIALS.update(REGISTERED_CREDENTIALS)


def render_header():
    """Render professional header with navigation and user menu"""
    col1, col2, col3 = st.columns([1.5, 2, 1])
    
    with col1:
        st.markdown("<h1>💰 MoneyTales</h1>", unsafe_allow_html=True)
    
    with col3:
        if st.session_state.authenticated:
            # Create a container for user menu with dropdown
            st.markdown("""
            <style>
            .user-menu-container {
                display: flex;
                justify-content: flex-end;
                align-items: center;
            }
            .user-dropdown {
                position: relative;
                display: inline-block;
            }
            .user-dropdown-content {
                display: none;
                position: absolute;
                right: 0;
                background-color: white;
                min-width: 200px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                padding: 12px 0;
                z-index: 1;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
            .user-dropdown-content a {
                color: #1e293b;
                padding: 12px 16px;
                text-decoration: none;
                display: block;
                transition: background-color 0.2s;
            }
            .user-dropdown-content a:hover {
                background-color: #f1f5f9;
            }
            </style>
            """, unsafe_allow_html=True)
            
            col_profile, col_menu = st.columns([2, 1], gap="small")
            
            with col_profile:
                st.markdown(f"""
                <div style='text-align: right; padding-top: 12px;'>
                    <div class='user-badge'>👤 {st.session_state.username}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_menu:
                if st.button("🚪 Sign Out", use_container_width=True, key="signout_btn"):
                    st.session_state.authenticated = False
                    st.session_state.username = None
                    st.session_state.user_id = None
                    st.session_state.user_age = None
                    st.session_state.current_quiz = None
                    st.session_state.available_topics = []
                    st.session_state.page = "explore"
                    st.success("✅ Signed out successfully!")
                    import time
                    time.sleep(1)
                    st.rerun()
    
    # Subheader text
    st.markdown("<p style='color: #64748b; font-size: 0.95rem; margin: 4px 0 16px 0;'>Learn Money Management the Fun Way</p>", unsafe_allow_html=True)
    
    st.markdown("---")


def login_page():
    """Login/Sign-in page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center; padding: 3rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>💰 MoneyTales</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;'>Financial Education for Kids</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tab selection for Sign In vs Register
        tab1, tab2 = st.tabs(["🔓 Sign In", "📝 Register"])
        
        with tab1:
            st.markdown("<h2 style='text-align: center;'>Sign In</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Welcome back! Sign in to continue learning</p>", unsafe_allow_html=True)
            
            # Login form
            with st.form("login_form"):
                username = st.text_input(
                    "👤 Username",
                    placeholder="Enter your username (e.g., alex, sam, jordan, casey)",
                    key="login_username"
                )
                
                password = st.text_input(
                    "🔐 Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password"
                )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    login_btn = st.form_submit_button("Sign In", use_container_width=True)
            
            if login_btn:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    # Try backend login first
                    try:
                        response = requests.post(
                            "http://localhost:8000/api/auth/login",
                            json={"username": username, "password": password},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            user_data = response.json()
                            st.session_state.authenticated = True
                            st.session_state.username = user_data["name"]
                            st.session_state.user_id = user_data["user_id"]
                            st.session_state.user_age = user_data.get("age", 10)
                            st.session_state.available_topics = []  # Reset topics to reload them
                            st.success(f"✅ Welcome, {user_data['name']}!")
                            st.rerun()
                        elif response.status_code == 401:
                            st.error("❌ Invalid username or password")
                        else:
                            st.error(f"❌ Login failed: {response.text}")
                    except Exception as e:
                        # Fallback to local credentials if backend unavailable
                        if username.lower() not in USERS_CREDENTIALS:
                            st.error("❌ Username not found")
                        elif USERS_CREDENTIALS[username.lower()]["password"] != password:
                            st.error("❌ Incorrect password")
                        else:
                            # Login successful with local credentials
                            user_data = USERS_CREDENTIALS[username.lower()]
                            st.session_state.authenticated = True
                            st.session_state.username = user_data["name"]
                            st.session_state.user_id = user_data["user_id"]
                            st.session_state.user_age = user_data.get("age", 10)
                            st.session_state.available_topics = []  # Reset topics to reload them
                            st.success(f"✅ Welcome, {user_data['name']}!")
                            st.rerun()
            
            # Demo credentials info
            st.markdown("---")
            st.markdown("<h4 style='text-align: center; color: #64748b;'>📝 Demo Credentials</h4>", unsafe_allow_html=True)
            
            demo_users = [
                ("👦 Alex", "alex / alex123"),
                ("👧 Sam", "sam / sam123"),
                ("👦 Jordan", "jordan / jordan123"),
                ("👧 Casey", "casey / casey123"),
            ]
            
            cols = st.columns(2, gap="medium")
            for idx, (name, cred) in enumerate(demo_users):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class='card' style='text-align: center; padding: 12px;'>
                        <p style='margin: 0 0 4px 0; font-weight: 600;'>{name}</p>
                        <p style='margin: 0; color: #64748b; font-size: 0.85rem;'><code>{cred}</code></p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("<h2 style='text-align: center;'>Create Account</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Join MoneyTales and start learning!</p>", unsafe_allow_html=True)
            
            # Registration form
            with st.form("register_form"):
                name = st.text_input(
                    "👤 Full Name",
                    placeholder="Enter your full name",
                    key="register_name"
                )
                
                username_reg = st.text_input(
                    "🔤 Username",
                    placeholder="Choose a username",
                    key="register_username"
                )
                
                age = st.slider(
                    "🎂 Age",
                    min_value=5,
                    max_value=100,
                    value=10,
                    key="register_age"
                )
                
                hobbies = st.text_input(
                    "🎯 Hobbies (comma-separated)",
                    placeholder="e.g., gaming, reading, sports",
                    key="register_hobbies"
                )
                
                password_reg = st.text_input(
                    "🔐 Password",
                    type="password",
                    placeholder="Enter a strong password",
                    key="register_password"
                )
                
                confirm_password = st.text_input(
                    "🔐 Confirm Password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="register_confirm"
                )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    register_btn = st.form_submit_button("Create Account", use_container_width=True)
            
            if register_btn:
                # Validation
                if not all([name, username_reg, password_reg, confirm_password, hobbies]):
                    st.error("❌ Please fill in all fields")
                elif len(username_reg) < 3:
                    st.error("❌ Username must be at least 3 characters")
                elif len(password_reg) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif password_reg != confirm_password:
                    st.error("❌ Passwords do not match")
                elif username_reg.lower() in USERS_CREDENTIALS:
                    st.error("❌ Username already exists")
                else:
                    # Generate user ID
                    import uuid
                    new_user_id = f"user_{uuid.uuid4().hex[:8]}"
                    
                    # Store hobbies as comma-separated string
                    hobbies_list = ", ".join([h.strip() for h in hobbies.split(",")])
                    
                    # Call backend to save user
                    try:
                        response = requests.post(
                            "http://localhost:8000/api/auth/register",
                            json={
                                "user_id": new_user_id,
                                "name": name,
                                "age": age,
                                "hobbies": hobbies_list,
                                "username": username_reg.lower(),
                                "password": password_reg
                            },
                            timeout=10
                        )
                        
                        if response.status_code == 200 or response.status_code == 201:
                            # Registration successful
                            user_data = response.json()
                            
                            # Add to local credentials for immediate use
                            USERS_CREDENTIALS[username_reg.lower()] = {
                                "user_id": user_data.get("user_id", new_user_id),
                                "name": name,
                                "password": password_reg,
                                "age": age
                            }
                            
                            st.success("✅ Account created successfully!")
                            st.info("Logging you in automatically...")
                            
                            # Auto-login after registration
                            import time
                            time.sleep(1)
                            
                            # Set session state for automatic login
                            st.session_state.authenticated = True
                            st.session_state.username = name
                            st.session_state.user_id = user_data.get("user_id", new_user_id)
                            st.session_state.user_age = age
                            st.session_state.available_topics = []
                            
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"❌ Registration failed: {response.text}")
                    except Exception as e:
                        st.warning(f"⚠️ Could not sync with server, but account created locally: {e}")
                        st.info("You can now sign in with your new account")
                        import time
                        time.sleep(2)
                        st.rerun()
        
        st.markdown("<div style='text-align: center; padding: 2rem 0; color: #94a3b8; font-size: 0.875rem;'><p>💰 <strong>MoneyTales</strong> v1.0</p></div>", unsafe_allow_html=True)


def render_navigation():
    """Render top navigation"""
    nav_items = [
        ("🏠 Explore", "explore"),
        ("📈 Progress", "progress"),
        ("🏅 Leaderboard", "leaderboard"),
        ("⚙️ Settings", "settings"),
    ]
    
    # Create 4 equal columns for navigation
    cols = st.columns(4)
    
    for i, (label, page_id) in enumerate(nav_items):
        with cols[i]:
            is_active = st.session_state.page == page_id
            btn_style = "color: white; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);" if is_active else ""
            
            if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.page = page_id
                st.rerun()
    
    st.markdown("---")


def explore_page():
    """Unified Home + Take Quiz page with age-based topic suggestions"""
    
    st.markdown("<h2>🎯 Take a Quiz</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 1rem; color: #64748b; margin: 0 0 1.5rem 0;'>Hello {st.session_state.username}! Choose a topic and start learning (difficulty will be auto-selected based on your performance)</p>", unsafe_allow_html=True)
    
    # Load topics based on age if not already loaded
    if not st.session_state.available_topics:
        with st.spinner("📚 Loading age-appropriate topics..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/topics/suggestions",
                    json={
                        "user_id": st.session_state.user_id,
                        "age": st.session_state.user_age
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.available_topics = data.get("topics", [])
                else:
                    st.session_state.available_topics = [
                        "Money Basics",
                        "Saving Money",
                        "Budgeting",
                        "Earning Money",
                        "Understanding Credit",
                        "Introduction to Investing"
                    ]
            except Exception as e:
                st.warning(f"Could not load topics from server: {e}")
                st.session_state.available_topics = [
                    "Money Basics",
                    "Saving Money",
                    "Budgeting",
                    "Earning Money",
                    "Understanding Credit",
                    "Introduction to Investing"
                ]
    
    # Quiz configuration section - only topic selection (no difficulty)
    col1, col2 = st.columns([2, 1], gap="small")
    
    with col1:
        topic = st.selectbox(
            "📚 Choose a Topic:",
            st.session_state.available_topics,
            key="topic_select"
        )
    
    with col2:
        st.markdown("<p style='margin: 0; color: transparent;'>Generate</p>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Generate Quiz", key="generate_quiz", use_container_width=True)
    
    if generate_btn:
        with st.spinner("✨ Generating personalized quiz..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/quiz/generate",
                    json={
                        "user_id": st.session_state.user_id,
                        "topic": topic
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.current_quiz = data
                    st.session_state.current_answers = []
                    st.rerun()
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
    
    # Display quiz if generated
    if st.session_state.current_quiz:
        quiz = st.session_state.current_quiz
        
        st.markdown("---")
        
        # Display difficulty tag
        difficulty = quiz.get('difficulty', 'medium').upper()
        difficulty_emoji = "🟢" if difficulty == "EASY" else ("🟡" if difficulty == "MEDIUM" else "🔴")
        st.markdown(f"""
        <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
            <span style='font-size: 1.5rem; margin-right: 0.5rem;'>{difficulty_emoji}</span>
            <span style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 0.875rem;'>
                {difficulty} Difficulty
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Display story in beautiful box
        st.markdown("<h3>📖 Your Story</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='story-box'>
            {quiz.get('story', '')}
        </div>
        """, unsafe_allow_html=True)
        
        # Display questions
        st.markdown("<h3>❓ Questions</h3>", unsafe_allow_html=True)
        
        questions = quiz.get("questions", [])
        answers = []
        
        for i, question in enumerate(questions):
            st.markdown(f"""
            <div class='question-box'>
                <strong>Question {i+1} of {len(questions)}</strong><br>
                <h4 style='margin: 8px 0 0 0;'>{question.get('question', '')}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            options = question.get("options", [])
            selected = st.radio(
                "Select your answer:",
                options=list(range(len(options))),
                format_func=lambda x: f"  {options[x]}",
                index=None,
                key=f"q_{i}_{st.session_state.current_quiz['request_id']}",
                label_visibility="collapsed"
            )
            
            answers.append(selected)
            st.session_state.current_answers = answers
        
        st.markdown("---")
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submit_btn = st.button("✅ Submit Answers", key="submit_quiz", use_container_width=True)
        
        if submit_btn:
            # Check if all questions answered
            if None in answers:
                st.error("⚠️ Please answer all questions before submitting!")
            else:
                with st.spinner("📊 Evaluating your answers..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/submit/answers",
                            json={
                                "user_id": st.session_state.user_id,
                                "questions": questions,
                                "answers": answers,
                                "topic": topic
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.quiz_result = result
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {e}")
    
    # Display results if available
    if hasattr(st.session_state, 'quiz_result') and st.session_state.quiz_result is not None:
        result = st.session_state.quiz_result
        
        st.markdown("---")
        st.markdown("<h2>🎉 Quiz Complete!</h2>", unsafe_allow_html=True)
        
        # Score cards with next difficulty recommendation
        next_diff = result.get('next_difficulty', 'medium').upper()
        diff_emoji = "🟢" if next_diff == "EASY" else ("🟡" if next_diff == "MEDIUM" else "🔴")
        
        col1, col2, col3, col4 = st.columns(4, gap="small")
        
        with col1:
            st.metric("📊 Score", f"{result.get('score', 0)}/100")
        with col2:
            st.metric("✨ Percentage", f"{result.get('percentage', 0):.0f}%")
        with col3:
            st.metric("💎 Points", f"+{result.get('points_earned', 0)}")
        with col4:
            if result.get('leveled_up'):
                st.metric("🎊 Level", f"Lvl {result.get('new_level', 1)}")
            else:
                st.metric("📈 Level", f"Lvl {result.get('current_level', 1)}")
        
        # Feedback with next difficulty recommendation
        st.markdown("")
        feedback_msg = result.get('feedback_message', result.get('feedback', ''))
        insight_msg = result.get('insight', '')
        st.info(f"💡 **Feedback:** {feedback_msg}\n\n📈 **Next Steps:** {insight_msg}\n\n{diff_emoji} **Next Quiz:** {next_diff}")
        
        # Badges
        badges = result.get('badges_earned', [])
        if badges:
            badge_names = ", ".join([b['name'] for b in badges])
            st.success(f"🏆 **New Badges Earned:** {badge_names}")
        
        # Detailed feedback
        st.markdown("---")
        st.markdown("<h3>📝 Detailed Review</h3>", unsafe_allow_html=True)
        
        for idx, qf in enumerate(result.get('question_feedback', [])):
            status_icon = "✅" if qf['is_correct'] else "❌"
            
            with st.expander(f"{status_icon} Question {idx+1}: {qf['question'][:60]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Your Answer:**")
                    st.info(qf['user_answer'])
                
                with col2:
                    if not qf['is_correct']:
                        st.write("**Correct Answer:**")
                        st.success(qf['correct_answer'])
                
                st.write("**Explanation:**")
                st.write(qf['explanation'])
        
        st.markdown("---")
        
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            if st.button("📚 Take Another Quiz", key="another_quiz", use_container_width=True):
                st.session_state.current_quiz = None
                st.session_state.quiz_result = None
                st.rerun()
        
        with col2:
            if st.button("📈 View Progress", key="view_progress", use_container_width=True):
                st.session_state.page = "progress"
                st.rerun()


def progress_page():
    """My Progress page"""
    st.markdown("<h2>📈 Your Progress</h2>", unsafe_allow_html=True)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/gamification/stats/{st.session_state.user_id}"
        )
        
        if response.status_code == 200:
            stats = response.json()
            
            # Stats cards
            col1, col2, col3, col4 = st.columns(4, gap="small")
            with col1:
                st.metric("⭐ Level", stats.get('level', 1))
            with col2:
                st.metric("💎 Points", stats.get('points', 0))
            with col3:
                st.metric("📚 Quizzes", stats.get('quizzes_completed', 0))
            with col4:
                st.metric("📊 Avg", f"{stats.get('average_score', 0):.0f}%")
            
            st.markdown("---")
            
            # Badges section
            st.markdown("<h3>🏆 Badges Earned</h3>", unsafe_allow_html=True)
            badges = stats.get('badges', [])
            if badges:
                badge_cols = st.columns(min(4, len(badges)), gap="small")
                for idx, badge in enumerate(badges):
                    with badge_cols[idx % 4]:
                        st.markdown(f"""
                        <div class='card' style='text-align: center; padding: 16px;'>
                            <div style='font-size: 2rem;'>🏅</div>
                            <p style='margin: 8px 0 0 0; font-weight: 600; font-size: 0.9rem;'>{badge}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No badges yet. Keep playing to earn them!")
            
            st.markdown("---")
            
            # Recent quizzes with difficulty tags
            st.markdown("<h3>📚 Recent Quizzes</h3>", unsafe_allow_html=True)
            recent = stats.get('recent_quizzes', [])
            if recent:
                for idx, quiz in enumerate(recent):
                    difficulty = quiz.get('difficulty', 'medium').upper()
                    difficulty_emoji = "🟢" if difficulty == "EASY" else ("🟡" if difficulty == "MEDIUM" else "🔴")
                    
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 0.8, 1], gap="small")
                    with col1:
                        st.write(f"**{quiz.get('topic')}**")
                    with col2:
                        st.write(f"**{quiz.get('percentage'):.0f}%**")
                    with col3:
                        st.markdown(f"{difficulty_emoji} {difficulty}")
                    with col4:
                        st.write(f"Lvl {quiz.get('level', 1)}")
                    with col5:
                        st.write(f"📅 {quiz.get('date', 'N/A')}")
                    if idx < len(recent) - 1:
                        st.divider()
            else:
                st.info("No quizzes taken yet. Take your first quiz!")
    
    except Exception as e:
        st.error(f"Error loading progress: {e}")


def leaderboard_page():
    """Leaderboard page with detailed stats"""
    st.markdown("<h2>🏅 Top Performers</h2>", unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{API_BASE_URL}/gamification/leaderboard")
        
        if response.status_code == 200:
            data = response.json()
            leaderboard = data.get('leaderboard', [])
            
            if leaderboard:
                st.markdown("""
                <style>
                .leaderboard-header {
                    display: grid;
                    grid-template-columns: 0.5fr 2fr 1fr 1fr 1fr 1fr;
                    gap: 1rem;
                    padding: 1rem;
                    background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                    border-radius: 8px;
                    font-weight: 600;
                    color: #1e293b;
                    margin-bottom: 1rem;
                }
                .leaderboard-row {
                    display: grid;
                    grid-template-columns: 0.5fr 2fr 1fr 1fr 1fr 1fr;
                    gap: 1rem;
                    padding: 1rem;
                    border-bottom: 1px solid #e2e8f0;
                    align-items: center;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Header
                st.markdown("""
                <div class='leaderboard-header'>
                    <div>Rank</div>
                    <div>Name</div>
                    <div>Level</div>
                    <div>Points</div>
                    <div>Quizzes</div>
                    <div>Avg Score</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Rows
                for idx, entry in enumerate(leaderboard):
                    medal = "🥇" if entry['rank'] == 1 else ("🥈" if entry['rank'] == 2 else ("🥉" if entry['rank'] == 3 else f"#{entry['rank']}"))
                    avg_score = entry.get('average_score', 0)
                    quizzes = entry.get('quizzes_completed', 0)
                    
                    st.markdown(f"""
                    <div class='leaderboard-row'>
                        <div style='font-size: 1.2rem;'>{medal}</div>
                        <div style='font-weight: 600;'>{entry['name']}</div>
                        <div>⭐ {entry['level']}</div>
                        <div>💎 {entry['points']}</div>
                        <div>📚 {quizzes}</div>
                        <div>📊 {avg_score:.0f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add user's own stats if not in top 10
                st.markdown("---")
                st.markdown("<h3>📍 Your Position</h3>", unsafe_allow_html=True)
                
                try:
                    user_response = requests.get(f"{API_BASE_URL}/gamification/stats/{st.session_state.user_id}")
                    if user_response.status_code == 200:
                        user_stats = user_response.json()
                        user_rank = user_stats.get('rank', 'N/A')
                        
                        col1, col2, col3, col4 = st.columns(4, gap="small")
                        with col1:
                            st.metric("Your Rank", user_rank)
                        with col2:
                            st.metric("Your Level", user_stats.get('level', 1))
                        with col3:
                            st.metric("Your Points", user_stats.get('points', 0))
                        with col4:
                            st.metric("Avg Score", f"{user_stats.get('average_score', 0):.0f}%")
                except:
                    pass
            else:
                st.info("No leaderboard data available yet.")
    
    except Exception as e:
        st.error(f"Error loading leaderboard: {e}")


def settings_page():
    """Settings page"""
    st.markdown("<h2>⚙️ Settings & Information</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown("<h3>👤 User Profile</h3>", unsafe_allow_html=True)
        st.write(f"**Current User:** {st.session_state.username}")
        st.write(f"**User ID:** {st.session_state.user_id}")
        st.markdown("")
        
        st.markdown("---")
        st.markdown("<h3 style='color: #ef4444;'>🚪 Sign Out</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; margin-bottom: 1rem;'>Sign out of your account and return to the login page</p>", unsafe_allow_html=True)
        
        if st.button("🚪 Sign Out", use_container_width=True, key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.session_state.current_quiz = None
            st.session_state.page = "explore"
            st.success("✅ Signed out successfully!")
            import time
            time.sleep(1)
            st.rerun()
    
    with col2:
        st.markdown("<h3>🔧 System Status</h3>", unsafe_allow_html=True)
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                st.success("✅ Backend Connected")
                st.write(f"**Database:** {health.get('database', 'Unknown')}")
                st.write(f"**RAG:** {health.get('rag', 'Unknown')}")
            else:
                st.error("❌ Backend Error")
        except:
            st.error("❌ Backend Disconnected")
    
    st.markdown("---")
    
    st.markdown("<h3>📚 About MoneyTales</h3>", unsafe_allow_html=True)
    st.markdown("""
    **MoneyTales** is an AI-powered financial education platform designed to teach children about money management through engaging stories and interactive quizzes.
    
    **Features:**
    - 📖 Personalized financial narratives
    - 🎮 Adaptive difficulty quizzes
    - 🏆 Gamification system
    - 📈 Progress tracking
    - 🤖 AI-powered content generation
    
    **Technology:**
    - Backend: FastAPI with 6 AI Agents
    - Frontend: Streamlit
    - Database: SQLite with WAL mode
    - RAG: Vector-based semantic search
    """)


def main():
    """Main application"""
    # Check if user is authenticated
    if not st.session_state.authenticated:
        login_page()
        return
    
    # User is authenticated, show main app
    render_header()
    render_navigation()
    
    # Route to appropriate page
    if st.session_state.page == "explore":
        explore_page()
    elif st.session_state.page == "progress":
        progress_page()
    elif st.session_state.page == "leaderboard":
        leaderboard_page()
    elif st.session_state.page == "settings":
        settings_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #94a3b8; font-size: 0.875rem;'>
        <p>💰 <strong>MoneyTales</strong> - Financial Education for Kids | v1.0</p>
        <p>Powered by AI Agents & RAG • FastAPI Backend • Streamlit Frontend</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
