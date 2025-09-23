from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from agents.content_generator import ContentGeneratorAgent
from agents.question_setter import QuestionSetterAgent
from agents.feedback_evaluator import FeedbackEvaluatorAgent
from database.session_manager import SessionManager
from utils.security import SecurityManager

# Configure page
st.set_page_config(
    page_title="AI Tutoring System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Ensure some sensible defaults used across UI
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = None
if 'requested_tab' not in st.session_state:
    st.session_state.requested_tab = None

# Initialize session state
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Initialize agents
@st.cache_resource
def initialize_agents():
    content_agent = ContentGeneratorAgent()
    question_agent = QuestionSetterAgent()
    feedback_agent = FeedbackEvaluatorAgent()
    return content_agent, question_agent, feedback_agent

content_agent, question_agent, feedback_agent = initialize_agents()

# Security manager
security = SecurityManager()

def authenticate_user():
    """Simple authentication interface"""
    st.sidebar.title("🔐 Authentication")
    
    if st.session_state.current_user is None:
        with st.sidebar:
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="e.g. learner01")
            password = st.text_input("Password", type="password", placeholder="Enter any password")
            st.caption("Demo login accepts any credentials")
            st.markdown("</div>", unsafe_allow_html=True)
        
        if st.sidebar.button("Login"):
            # Basic authentication (in production, use proper authentication)
            if username and password:
                sanitized_username = security.sanitize_input(username)
                st.session_state.current_user = sanitized_username
                st.sidebar.success(f"Welcome, {sanitized_username}!")
                st.rerun()
            else:
                st.sidebar.error("Please enter valid credentials")
    else:
        with st.sidebar:
            st.markdown(f"**👤 {st.session_state.current_user}**")
            st.caption("Logged in")
        if st.sidebar.button("Logout"):
            st.session_state.current_user = None
            st.rerun()

    # Sidebar navigation
    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Navigation")
    nav_choice = st.sidebar.radio(
        "Go to",
        options=[
            "📚 Content Generator",
            "❓ Question Setter",
            "✅ Feedback Evaluator",
            "📊 Progress Tracking",
            "🔍 Knowledge Base",
            "🔄 Adaptive Learning",
        ],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state.nav_choice = nav_choice

def main_interface():
    """Main tutoring interface"""
    render_header()

    # Route based on sidebar selection for a more intuitive UX
    choice = st.session_state.get("nav_choice", "� Content Generator")
    if choice.startswith("📚"):
        content_generator_interface()
    elif choice.startswith("❓"):
        question_setter_interface()
    elif choice.startswith("✅"):
        feedback_evaluator_interface()
    elif choice.startswith("📊"):
        progress_tracking_interface()
    elif choice.startswith("🔍"):
        knowledge_base_interface()
    elif choice.startswith("🔄"):
        adaptive_learning_interface()

    # Optional: quick adaptive button at bottom
    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("🔄 Adaptive Mode"):
            st.session_state.nav_choice = "🔄 Adaptive Learning"
            st.rerun()

def render_header():
    """Hero header with quick stats and theme toggle"""
    st.markdown(
        """
        <div class="main-header">
            <h1>🎓 AI Tutoring System</h1>
            <div class="subtitle">Multi‑agent learning companion: generate content, practice with questions, and get feedback.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick metrics row
    col1, col2, col3, col4 = st.columns(4)
    user = st.session_state.get('current_user')
    progress = st.session_state.session_manager.get_user_progress(user) if user else {}
    with col1:
        st.metric("📚 Content", progress.get('content_count', 0))
    with col2:
        st.metric("❓ Answered", progress.get('questions_answered', 0))
    with col3:
        st.metric("📊 Avg Score", f"{progress.get('average_score', 0):.1f}%")
    with col4:
        st.metric("🔥 Streak", f"{progress.get('study_streak', 0)} days")

def content_generator_interface():
    """Enhanced Content Generator Agent Interface - Teacher Role"""
    st.header("👨‍🏫 Content Generator (Teacher)")
    st.markdown("Create student‑friendly study materials with sources, key concepts, and study aids.")
    st.markdown("<div class='professional-card'>", unsafe_allow_html=True)
    
    # Helpful quick-start chips (handle before widgets so state is set prior to instantiation)
    st.caption("Try a quick topic:")
    chip_cols = st.columns(6)
    sample_topics = [
        "Photosynthesis",
        "Linear Algebra: Eigenvalues",
        "Python Lists vs Tuples",
        "World War II: Causes",
        "Machine Learning Basics",
        "Chemical Bonding"
    ]
    for i, s in enumerate(sample_topics):
        with chip_cols[i % 6]:
            if st.button(f"{s}", key=f"chip_{i}"):
                st.session_state["topic_input"] = s
                st.rerun()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("📖 Enter Topic", key="topic_input", placeholder="e.g., Photosynthesis, Machine Learning, World War II")
        
        learning_objectives = st.text_area(
            "🎯 Learning Objectives (Optional)",
            placeholder="What should students understand after studying this topic?",
            height=80
        )
    
    with col2:
        difficulty = st.select_slider("📊 Difficulty Level", 
                                    options=["Beginner", "Intermediate", "Advanced"])
        
        subject = st.selectbox("🎯 Subject Area", [
            "Science", "Mathematics", "Computer Science", "History", 
            "Literature", "Languages", "Business", "Arts", "General"
        ])
        
        content_type = st.selectbox("📋 Content Type", [
            "Study Notes", "Tutorial", "Explanation", "Summary", "Comprehensive Guide"
        ])
    
    # (Chips moved above so they don't mutate widget state post-instantiation)

    # Advanced options
    with st.expander("🔧 Advanced Options"):
        include_flashcards = st.checkbox("Generate Flashcards", value=True)
        include_diagrams = st.checkbox("Suggest Diagrams", value=True)
        source_quality = st.selectbox(
            "Source Preference",
            options=["Academic & Educational", "Academic Only", "Educational Only"]
        )
    
    if st.button("🚀 Generate Study Materials", type="primary"):
        if topic:
            with st.spinner("👨‍🏫 Teacher is creating comprehensive study materials..."):
                try:
                    # Sanitize input
                    clean_topic = security.sanitize_input(topic)
                    # Parse learning objectives
                    objectives = [obj.strip() for obj in learning_objectives.split('\n') if obj.strip()] if learning_objectives else None
                    # Generate enhanced content using updated agent
                    content_result = content_agent.generate_content(
                        topic=clean_topic,
                        difficulty=difficulty,
                        subject=subject,
                        content_type=content_type,
                        learning_objectives=objectives
                    )
                    
                    st.success("✅ Study materials created successfully!")
                    
                    # Handle both old and new content format
                    if isinstance(content_result, dict):
                        main_content = content_result.get('content', str(content_result))
                        study_materials = content_result.get('study_materials', {})
                        key_concepts = content_result.get('key_concepts', [])
                        objectives_list = content_result.get('learning_objectives', objectives or [])
                        source_quality_score = content_result.get('sources', {}).get('quality_score', 0.5)
                    else:
                        # Fallback for old format
                        main_content = content_result
                        study_materials = {}
                        key_concepts = []
                        objectives_list = objectives or []
                        source_quality_score = 0.5
                    
                    # Display main content
                    with st.expander("📖 Study Notes", expanded=True):
                        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                        st.markdown(main_content)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Display study materials in tabs
                    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Key Concepts", "🃏 Flashcards", "📊 Objectives", "🎨 Study Aids"])
                    
                    with tab1:
                        st.markdown("#### 🔑 Key Concepts Identified")
                        if key_concepts:
                            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                            for i, concept in enumerate(key_concepts[:10], 1):
                                st.markdown(f"{i}. **{concept}**")
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.info("Key concepts will be extracted from the content")
                    
                    with tab2:
                        if include_flashcards:
                            st.markdown("#### 🃏 Generated Flashcards")
                            flashcards = study_materials.get('flashcards', [])
                            if flashcards:
                                for i, card in enumerate(flashcards[:8]):
                                    with st.expander(f"Flashcard {i+1}: {card.get('term', f'Concept {i+1}')}" ):
                                        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                                        st.markdown(f"**Definition:** {card.get('definition', 'Key concept in the topic')}")
                                        st.markdown(f"**Category:** <span class='badge badge-secondary'>{card.get('category', 'CONCEPT')}</span>", unsafe_allow_html=True)
                                        st.markdown("</div>", unsafe_allow_html=True)
                            else:
                                st.info("Flashcards will be generated based on key concepts")
                    
                    with tab3:
                        st.markdown("#### 📚 Learning Objectives")
                        if objectives_list:
                            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                            for i, obj in enumerate(objectives_list, 1):
                                st.markdown(f"{i}. {obj}")
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.info("Learning objectives will be created based on the topic")
                    
                    with tab4:
                        if include_diagrams:
                            st.markdown("#### 🎨 Suggested Diagrams")
                            diagram_suggestions = study_materials.get('diagram_suggestions', [])
                            if diagram_suggestions:
                                st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                                for diagram in diagram_suggestions:
                                    st.markdown(f"• **{diagram}** - Recommended for visual learning")
                                st.markdown("</div>", unsafe_allow_html=True)
                            else:
                                st.info("Diagram suggestions will be provided based on topic analysis")
                        
                        st.markdown("#### 📝 Study Notes Summary")
                        bullet_notes = study_materials.get('study_notes', '')
                        if bullet_notes:
                            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                            st.markdown(bullet_notes)
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.info("Study notes summary will be created from main content")
                    
                    # Source quality indicator
                    quality_color = "🟢" if source_quality_score > 0.7 else "🟡" if source_quality_score > 0.4 else "🔴"
                    st.markdown(f"**Source Quality:** {quality_color} {source_quality_score:.1%}")
                    
                    # Save enhanced content to session
                    st.session_state.session_manager.save_content(
                        user=st.session_state.current_user,
                        topic=clean_topic,
                        content=main_content,
                        metadata={
                            "difficulty": difficulty,
                            "subject": subject,
                            "content_type": content_type,
                            "key_concepts": key_concepts,
                            "learning_objectives": objectives_list,
                            "source_quality": source_quality_score,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    
                    # Store in session state for workflow continuation
                    st.session_state.last_generated_content = content_result
                    st.session_state.last_content_topic = clean_topic
                    
                    # Quick action to continue workflow
                    st.markdown("### 🔄 Next Step")
                    col1, col2 = st.columns(2)
                    with col2:
                        if st.button("📊 View Progress", type="secondary"):
                            st.session_state.nav_choice = "❓ Question Setter"
                            st.rerun()
                    with col2:
                        if st.button("� View Progress", type="secondary"):
                            st.session_state.nav_choice = "📊 Progress Tracking"
                            st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error generating content: {str(e)}")
                    st.info("The system will fall back to basic content generation if enhanced features aren't available.")
        else:
            st.warning("⚠️ Please enter a topic to generate educational material.")

def question_setter_interface():
    """Enhanced Question Setter Agent Interface - Exam Designer Role"""
    st.header("📝 Question Setter (Exam Designer)")
    st.markdown("Create MCQ, T/F, and short answers using Bloom’s taxonomy and difficulty tuning.")
    st.markdown("<div class='professional-card'>", unsafe_allow_html=True)

    # Get recent content from session
    recent_content = st.session_state.session_manager.get_recent_content(
        st.session_state.current_user
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        if recent_content:
            selected_content = st.selectbox(
                "📚 Select Content for Questions",
                options=list(recent_content.keys()),
                format_func=lambda x: f"{x[:50]}..." if len(x) > 50 else x,
            )
        else:
            st.info("📝 Generate some content first to create questions.")
            selected_content = None

        custom_content = st.text_area(
            "📝 Or Enter Custom Content",
            height=150,
            placeholder="Paste or enter the content you want to generate questions from...",
        )

    with col2:
        question_count = st.number_input(
            "🔢 Number of Questions",
            min_value=1,
            max_value=20,
            value=5,
            help="How many questions to generate",
        )
        question_types = st.multiselect(
            "❓ Question Types",
            [
                "Multiple Choice",
                "True/False",
                "Short Answer",
                "Essay",
                "Fill in the Blank",
            ],
            default=["Multiple Choice", "Short Answer"],
        )

    # Enhanced Bloom's Taxonomy and Difficulty Controls
    with st.expander("🎯 Advanced Question Settings"):
        col1_exp, col2_exp = st.columns(2)

        with col1_exp:
            st.markdown("**📚 Bloom's Taxonomy Levels**")
            bloom_levels = st.multiselect(
                "Select Learning Levels",
                ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
                default=["Remember", "Understand", "Apply", "Analyze"],
                help="Target specific cognitive learning levels",
            )

        with col2_exp:
            st.markdown("**⚖️ Difficulty Distribution**")
            easy_pct = st.slider("Easy %", 0, 100, 30)
            medium_pct = st.slider("Medium %", 0, 100, 50)
            hard_pct = 100 - easy_pct - medium_pct
            st.write(f"Hard: {hard_pct}%")

            difficulty_distribution = {
                "Easy": easy_pct / 100,
                "Medium": medium_pct / 100,
                "Hard": hard_pct / 100,
            }

        generate_distractors = st.checkbox(
            "Generate Smart Distractors for MCQ", value=True
        )
        adaptive_difficulty = st.checkbox(
            "Adaptive Difficulty Based on Performance", value=True
        )

    if st.button("🎯 Generate Questions", type="primary"):
        content_to_use = None

        if custom_content:
            content_to_use = security.sanitize_input(custom_content)
        elif selected_content and recent_content:
            content_to_use = recent_content[selected_content]

        if content_to_use:
            with st.spinner("🤖 AI is generating questions..."):
                try:
                    # Prefer structured last_generated_content if available
                    if hasattr(st.session_state, "last_generated_content") and isinstance(
                        st.session_state.last_generated_content, dict
                    ):
                        content_input = st.session_state.last_generated_content
                    else:
                        content_input = content_to_use

                    # Generate questions with enhanced parameters
                    questions_result = question_agent.generate_questions(
                        content=content_input,
                        question_count=question_count,
                        question_types=question_types,
                        difficulty_distribution=difficulty_distribution
                        if "difficulty_distribution" in locals()
                        else None,
                        bloom_levels=bloom_levels if "bloom_levels" in locals() else None,
                    )

                    st.success("✅ Questions generated successfully!")

                    # Handle both old and new question format
                    if isinstance(questions_result, dict):
                        questions = questions_result.get("questions", [])
                        metadata = questions_result.get("metadata", {})

                        # Display metadata summary
                        if metadata:
                            st.markdown("### 📊 Question Bank Summary")
                            col1_meta, col2_meta, col3_meta = st.columns(3)

                            with col1_meta:
                                st.metric(
                                    "Total Questions",
                                    metadata.get("total_count", len(questions)),
                                )

                            with col2_meta:
                                difficulty_dist = metadata.get(
                                    "difficulty_distribution", {}
                                )
                                if difficulty_dist:
                                    st.write("**Difficulty Mix:**")
                                    for diff, pct in difficulty_dist.items():
                                        st.write(f"• {diff}: {pct:.1%}")

                            with col3_meta:
                                bloom_levels_used = metadata.get("bloom_levels", [])
                                if bloom_levels_used:
                                    st.write("**Bloom Levels:**")
                                    for level in bloom_levels_used[:3]:
                                        st.write(f"• {level}")
                    else:
                        questions = questions_result
                        metadata = {}

                    # Display questions
                    for i, question in enumerate(questions, 1):
                        # Enhanced question display with metadata
                        difficulty_badge = ""
                        bloom_badge = ""

                        if question.get("difficulty"):
                            diff_color = {
                                "Easy": "🟢",
                                "Medium": "🟡",
                                "Hard": "🔴",
                            }.get(question["difficulty"], "⚪")
                            difficulty_badge = f"{diff_color} {question['difficulty']}"

                        if question.get("bloom_level"):
                            bloom_badge = f"📚 {question['bloom_level']}"

                        header = f"❓ Question {i}: {question.get('type', 'Unknown')} "
                        badge_html = (
                            f"<span class='badge badge-secondary'>{difficulty_badge}</span> "
                            if difficulty_badge
                            else ""
                        )
                        badge_html += (
                            f"<span class='badge badge-secondary'>{bloom_badge}</span>"
                            if bloom_badge
                            else ""
                        )
                        with st.expander(header + "  " + badge_html, expanded=True):
                            st.markdown(
                                "<div class='question-container'>",
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"**Question:** {question['question']}")

                            if question["type"] == "Multiple Choice":
                                for j, option in enumerate(
                                    question.get("options", []), 1
                                ):
                                    st.markdown(f"{chr(64+j)}. {option}")
                                st.markdown(
                                    f"**Correct Answer:** {question.get('correct_answer', 'N/A')}"
                                )

                            elif question["type"] == "True/False":
                                st.markdown(
                                    f"**Correct Answer:** {question.get('correct_answer', 'N/A')}"
                                )

                            if "explanation" in question:
                                st.markdown(
                                    f"**Explanation:** {question['explanation']}"
                                )
                            st.markdown("</div>", unsafe_allow_html=True)

                    # Save questions to session state for adaptive workflow
                    st.session_state.last_generated_questions = questions_result
                    st.session_state.last_questions_metadata = metadata

                    # Save questions
                    st.session_state.session_manager.save_questions(
                        user=st.session_state.current_user,
                        questions=questions,
                        content_source=selected_content or "Custom Content",
                    )

                    # Continue workflow
                    st.markdown("### 🔄 Next Step")
                    col1_workflow, col2_workflow = st.columns(2)
                    with col1_workflow:
                        if st.button("➡️ Go to Feedback Evaluator", type="secondary"):
                            st.session_state.nav_choice = "✅ Feedback Evaluator"
                            st.rerun()
                    with col2_workflow:
                        if st.button("📊 View Progress", type="secondary"):
                            st.session_state.nav_choice = "📊 Progress Tracking"
                            st.rerun()

                except Exception as e:
                    st.error(f"❌ Error generating questions: {str(e)}")
        else:
            st.warning(
                "⚠️ Please select content or enter custom content to generate questions."
            )

def adaptive_learning_interface():
    """Adaptive Learning Workflow - Complete learning loop with difficulty adjustment"""
    st.header("🔄 Adaptive Learning")
    st.markdown("Adaptive system that adjusts difficulty and focus areas based on your performance.")
    
    # Check if we have content and questions
    if not hasattr(st.session_state, 'last_generated_content'):
        st.info("Start by generating content in the Content Generator to begin the adaptive learning workflow.")
        if st.button("🚀 Go to Content Generator"):
            st.session_state.nav_choice = "📚 Content Generator"
            st.rerun()
        return
    
    # Current learning state
    st.markdown("### 🎯 Current Learning State")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_topic = getattr(st.session_state, 'last_content_topic', 'Unknown Topic')
        st.metric("📚 Current Topic", current_topic)
    
    with col2:
        questions_available = len(getattr(st.session_state, 'last_generated_questions', {}).get('questions', []))
        st.metric("❓ Questions Available", questions_available)
    
    with col3:
        performance_history = getattr(st.session_state, 'performance_history', [])
        if performance_history:
            avg_performance = sum(p.get('overall_score', 0) for p in performance_history[-5:]) / len(performance_history[-5:])
        else:
            avg_performance = 0
        st.metric("📊 Recent Avg Score", f"{avg_performance:.1f}%")
    
    # Adaptive recommendations
    st.markdown("### 🤖 AI Recommendations")
    
    # Analyze performance and suggest next steps
    if performance_history:
        latest_performance = performance_history[-1]
        
        if latest_performance.get('overall_score', 0) >= 80:
            st.success("🌟 **Excellent Performance!** Ready for advanced challenges.")
            recommended_difficulty = "Hard"
            recommended_action = "Advance to higher-level concepts or explore related topics"
        elif latest_performance.get('overall_score', 0) >= 60:
            st.info("📈 **Good Progress!** Ready for moderate challenges.")
            recommended_difficulty = "Medium"
            recommended_action = "Continue with current level, add some challenging questions"
        else:
            st.warning("📖 **Need More Practice.** Focus on fundamentals.")
            recommended_difficulty = "Easy"
            recommended_action = "Review basics and practice with easier questions"
        
        st.markdown(f"**Recommended Next Steps:** {recommended_action}")
        st.markdown(f"**Suggested Difficulty:** {recommended_difficulty}")
    else:
        st.info("Take your first quiz to get personalized recommendations!")
    
    # Interactive learning actions
    st.markdown("### 🎮 Learning Actions")
    
    col1_action, col2_action, col3_action = st.columns(3)
    
    with col1_action:
        if st.button("📚 Generate New Content", type="primary"):
            # Adaptive content generation based on performance
            weak_concepts = []
            if performance_history:
                latest = performance_history[-1]
                weak_concepts = latest.get('improvement_areas', [])
            
            st.session_state.adaptive_mode = True
            st.session_state.focus_areas = weak_concepts
            st.success("🔄 Adaptive mode activated! Content will focus on your weak areas.")
    
    with col2_action:
        if st.button("❓ Generate Adaptive Questions", type="secondary"):
            # Adjust question difficulty based on performance
            if performance_history:
                avg_score = sum(p.get('overall_score', 0) for p in performance_history[-3:]) / max(len(performance_history[-3:]), 1)
                
                if avg_score >= 85:
                    difficulty_dist = {"Easy": 0.1, "Medium": 0.4, "Hard": 0.5}
                    bloom_focus = ["Apply", "Analyze", "Evaluate", "Create"]
                elif avg_score >= 70:
                    difficulty_dist = {"Easy": 0.2, "Medium": 0.6, "Hard": 0.2}
                    bloom_focus = ["Understand", "Apply", "Analyze"]
                else:
                    difficulty_dist = {"Easy": 0.5, "Medium": 0.4, "Hard": 0.1}
                    bloom_focus = ["Remember", "Understand", "Apply"]
                
                st.session_state.adaptive_difficulty = difficulty_dist
                st.session_state.adaptive_bloom = bloom_focus
                st.success(f"🎯 Questions will be adapted: {int(difficulty_dist['Hard']*100)}% Hard, {int(difficulty_dist['Medium']*100)}% Medium, {int(difficulty_dist['Easy']*100)}% Easy")
    
    with col3_action:
        if st.button("📋 Take Adaptive Quiz", type="secondary"):
            # Start an adaptive quiz session
            st.session_state.quiz_mode = "adaptive"
            st.info("🚀 Starting adaptive quiz based on your learning profile...")
    
    # Performance analytics
    if performance_history:
        st.markdown("### 📈 Learning Analytics")
        
        # Concept mastery
        st.markdown("#### 🎯 Recent Concept Performance")
        latest_concepts = performance_history[-1].get('concept_scores', {})
        if latest_concepts:
            for concept, score in list(latest_concepts.items())[:5]:
                progress_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                st.markdown(f"{progress_color} **{concept}**: {score:.1f}%")
    
    # Learning path recommendations
    st.markdown("### 🛤️ Suggested Learning Path")
    
    if current_topic and performance_history:
        latest_performance = performance_history[-1]
        strengths = latest_performance.get('strengths', [])
        improvements = latest_performance.get('improvement_areas', [])
        
        if strengths:
            st.markdown("**Build on your strengths:**")
            for strength in strengths[:3]:
                st.markdown(f"• {strength}")
        
        if improvements:
            st.markdown("**Focus areas for improvement:**")
            for improvement in improvements[:3]:
                st.markdown(f"• {improvement}")
    else:
        st.info("Complete a quiz to get personalized learning path recommendations.")

def feedback_evaluator_interface():
    """Feedback Evaluator Agent Interface"""
    st.header("✅ Feedback Evaluator")
    st.markdown("Get personalized feedback on your answers and performance.")
    st.markdown("<div class='professional-card'>", unsafe_allow_html=True)
    
    # Get recent questions
    recent_questions = st.session_state.session_manager.get_recent_questions(
        st.session_state.current_user
    )
    
    if not recent_questions:
        st.info("📝 Generate some questions first to receive feedback.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_question_set = st.selectbox(
            "❓ Select Question Set",
            options=list(recent_questions.keys())
        )
        
        if selected_question_set:
            questions = recent_questions[selected_question_set]
            
            st.markdown("### 📝 Answer the Questions")
            user_answers = {}
            
            # Initialize variables to avoid unbound errors
            
            for i, question in enumerate(questions):
                st.markdown(f"**Question {i+1}:** {question['question']}")
                
                if question['type'] == 'Multiple Choice':
                    options = question.get('options', [])
                    answer = st.radio(
                        f"Select answer for Q{i+1}:",
                        options,
                        key=f"q_{i}",
                        label_visibility="collapsed"
                    )
                    user_answers[i] = answer
                
                elif question['type'] == 'True/False':
                    answer = st.radio(
                        f"Select answer for Q{i+1}:",
                        ["True", "False"],
                        key=f"q_{i}",
                        label_visibility="collapsed"
                    )
                    user_answers[i] = answer
                
                elif question['type'] in ['Short Answer', 'Essay']:
                    answer = st.text_area(
                        f"Your answer for Q{i+1}:",
                        key=f"q_{i}",
                        label_visibility="collapsed"
                    )
                    user_answers[i] = security.sanitize_input(answer) if answer else ""
                
                st.markdown("---")
    
    with col2:
        feedback_type = st.selectbox(
            "🎯 Feedback Type",
            ["Detailed", "Summary", "Constructive", "Encouraging"]
        )
        
        include_suggestions = st.checkbox("💡 Include Study Suggestions", value=True)
    
    if st.button("📊 Evaluate & Get Feedback", type="primary"):
        if 'user_answers' in locals() and user_answers and 'questions' in locals() and questions:
            with st.spinner("🤖 AI is evaluating your answers..."):
                try:
                    feedback = feedback_agent.evaluate_answers(
                        questions=questions,
                        user_answers=user_answers,
                        feedback_type=feedback_type,
                        include_suggestions=include_suggestions
                    )
                    
                    st.success("✅ Feedback generated successfully!")
                    
                    # Display overall score
                    col_score1, col_score2, col_score3 = st.columns(3)
                    
                    with col_score1:
                        st.metric("📊 Overall Score", f"{feedback.get('overall_score', 0)}%")
                    
                    with col_score2:
                        total_questions = len(questions) if 'questions' in locals() and questions else 0
                        st.metric("✅ Correct Answers", f"{feedback.get('correct_count', 0)}/{total_questions}")
                    
                    with col_score3:
                        performance = "Excellent" if feedback.get('overall_score', 0) >= 80 else "Good" if feedback.get('overall_score', 0) >= 60 else "Needs Improvement"
                        st.metric("🎯 Performance", performance)
                    
                    # Detailed feedback
                    with st.expander("📋 Detailed Feedback", expanded=True):
                        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                        st.markdown(feedback.get('detailed_feedback', ''))
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    if include_suggestions and 'study_suggestions' in feedback:
                        with st.expander("💡 Study Suggestions", expanded=True):
                            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                            st.markdown(feedback['study_suggestions'])
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Save feedback
                    st.session_state.session_manager.save_feedback(
                        user=st.session_state.current_user,
                        feedback=feedback,
                        question_set=selected_question_set
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error evaluating answers: {str(e)}")
        else:
            st.warning("⚠️ Please answer at least one question to get feedback.")

def progress_tracking_interface():
    """Progress Tracking and Analytics Interface"""
    st.header("📊 Progress Tracking & Analytics")
    st.markdown("Monitor your learning progress and performance over time.")
    st.markdown("<div class='professional-card'>", unsafe_allow_html=True)
    
    # Get user progress data
    progress_data = st.session_state.session_manager.get_user_progress(
        st.session_state.current_user
    )
    
    if not progress_data:
        st.info("📈 Start learning to see your progress here!")
        return
    
    # Progress metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Content Generated", progress_data.get('content_count', 0))
    
    with col2:
        st.metric("❓ Questions Answered", progress_data.get('questions_answered', 0))
    
    with col3:
        avg_score = progress_data.get('average_score', 0)
        st.metric("📊 Average Score", f"{avg_score:.1f}%")
    
    with col4:
        study_streak = progress_data.get('study_streak', 0)
        st.metric("🔥 Study Streak", f"{study_streak} days")
    
    # Performance chart
    if 'score_history' in progress_data and progress_data['score_history']:
        st.markdown("### 📈 Performance Over Time")
        df = pd.DataFrame(progress_data['score_history'])
        fig = px.line(
            df,
            x='date',
            y='score',
            title='Score Progression',
            labels={'score': 'Score (%)', 'date': 'Date'}
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No score history yet. Answer some questions to track progress over time.")
    
    # Subject performance
    if 'subject_performance' in progress_data and progress_data['subject_performance']:
        st.markdown("### 🎯 Performance by Subject")
        subjects = list(progress_data['subject_performance'].keys())
        scores = list(progress_data['subject_performance'].values())
        df_subjects = pd.DataFrame({
            'Subject': subjects,
            'Average Score': scores
        })
        fig = px.bar(
            df_subjects,
            x='Subject',
            y='Average Score',
            title='Average Score by Subject',
            labels={'Average Score': 'Average Score (%)', 'Subject': 'Subject'}
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No subject performance data yet.")
    
    # Recent activity
    st.markdown("### 📋 Recent Activity")
    recent_activity = progress_data.get('recent_activity', [])
    
    if recent_activity:
        for activity in recent_activity[-10:]:  # Show last 10 activities
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{activity['type']}:** {activity['description']}")
                
                with col2:
                    st.markdown(f"📅 {activity['date']}")
                
                with col3:
                    if 'score' in activity:
                        st.markdown(f"📊 {activity['score']}%")
    else:
        st.info("No recent activity to display.")

def knowledge_base_interface():
    """Knowledge Base and Information Retrieval Interface"""
    st.header("🔍 Knowledge Base Search")
    st.markdown("Search and explore educational resources and knowledge.")
    st.markdown("<div class='professional-card'>", unsafe_allow_html=True)
    
    from utils.information_retrieval import InformationRetrieval
    ir_system = InformationRetrieval()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search Knowledge Base",
            placeholder="Enter your search query..."
        )
    
    with col2:
        search_type = st.selectbox(
            "🎯 Search Type",
            ["General", "Definitions", "Examples", "Tutorials"]
        )
    
    if st.button("🔍 Search", type="primary"):
        if search_query:
            with st.spinner("🔍 Searching knowledge base..."):
                try:
                    clean_query = security.sanitize_input(search_query)
                    results = ir_system.search(clean_query, search_type)
                    
                    if results:
                        st.success(f"✅ Found {len(results)} results")
                        
                        for i, result in enumerate(results, 1):
                            with st.expander(f"📖 Result {i}: {result['title']}", expanded=i==1):
                                st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                                st.markdown(f"**Source:** {result.get('source', 'AI Generated')}")
                                st.markdown(f"**Relevance:** {result.get('relevance_score', 0):.2f}")
                                st.markdown("---")
                                st.markdown(result['content'])
                                
                                if result.get('related_topics'):
                                    st.markdown("**Related Topics:**")
                                    for topic in result['related_topics']:
                                        st.markdown(f"- {topic}")
                                st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("🔍 No results found. Try different keywords.")
                        
                except Exception as e:
                    st.error(f"❌ Search error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a search query.")
    
    # Popular topics
    st.markdown("### 🔥 Popular Topics")
    popular_topics = [
        "Python Programming", "Machine Learning", "Calculus", "Data Structures",
        "World War II", "Shakespeare", "Chemistry Basics", "Linear Algebra"
    ]
    
    cols = st.columns(4)
    for i, topic in enumerate(popular_topics):
        with cols[i % 4]:
            if st.button(f"📚 {topic}", key=f"topic_{i}"):
                st.session_state.search_query = topic
                st.rerun()

# Main application flow
def main():
    authenticate_user()
    
    if st.session_state.current_user:
        main_interface()
    else:
        render_header()
        st.markdown(
            """
            <div class='professional-card'>
            <h3>🚀 Multi‑Agent Educational Platform</h3>
            <p>
            Generate personalized study notes, practice questions, and receive instant feedback — all in one place.
            </p>
            <ul>
              <li>🤖 AI‑powered content and assessments</li>
              <li>📊 Progress tracking and analytics</li>
              <li>🔍 Built‑in knowledge base search</li>
              <li>🎯 Adaptive learning recommendations</li>
            </ul>
            <p><em>Log in from the left sidebar to get started.</em></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    main()
