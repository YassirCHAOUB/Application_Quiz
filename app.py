import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from models import QuestionDataset, QuizGenerator, QuizCorrector

class QuizView:
    """
    Handles all Streamlit rendering and user interactions.
    """
    def __init__(self, dataset):
        self.dataset = dataset
        self.all_tags = dataset.get_all_tags()
        
        # Initialize session state
        if 'quiz_generated' not in st.session_state:
            st.session_state.quiz_generated = False
        if 'questions' not in st.session_state:
            st.session_state.questions = []
        if 'user_answers' not in st.session_state:
            st.session_state.user_answers = {}
        if 'quiz_corrected' not in st.session_state:
            st.session_state.quiz_corrected = False
        if 'results' not in st.session_state:
            st.session_state.results = None

    def reset_quiz(self):
        """Reset all quiz-related session state."""
        st.session_state.quiz_generated = False
        st.session_state.questions = []
        st.session_state.user_answers = {}
        st.session_state.quiz_corrected = False
        st.session_state.results = None
        st.success("✓ Quiz reset successfully!")
        st.rerun()

    def select_fields(self):
        """Display field selection UI and return selected fields."""
        st.sidebar.header("📚 Quiz Configuration")
        
        # Tag selection
        selected_tags = st.sidebar.multiselect(
            "Select Topics:",
            options=self.all_tags,
            default=None,
            help="Select one or more topics. Leave empty to include all topics."
        )
        
        # Number of questions
        num_questions = st.sidebar.slider(
            "Number of Questions:",
            min_value=5,
            max_value=50,
            value=10,
            step=5
        )
        
        st.session_state.num_questions = num_questions
        
        return selected_tags

    def generate_quiz(self, selected_fields):
        """Generate a new quiz based on selected fields."""
        generator = QuizGenerator(self.dataset)
        questions = generator.generate_quiz(
            selected_tags=selected_fields,
            num_questions=st.session_state.num_questions
        )
        
        if not questions:
            st.error("❌ No questions found for the selected topics!")
            return
        
        st.session_state.questions = questions
        st.session_state.quiz_generated = True
        st.session_state.user_answers = {}
        st.session_state.quiz_corrected = False
        st.session_state.results = None
        st.success(f"✓ Generated quiz with {len(questions)} questions!")
        st.rerun()

    def show_quiz(self):
        """Display quiz questions and collect answers."""
        if not st.session_state.quiz_generated:
            st.info("👆 Configure your quiz in the sidebar and click 'Generate Quiz' to start!")
            return
        
        if st.session_state.quiz_corrected:
            # Show results
            self._show_results()
            return
        
        st.header("📝 Quiz Questions")
        st.markdown("---")
        
        questions = st.session_state.questions
        
        for idx, question in enumerate(questions):
            # Question container
            with st.container():
                col1, col2 = st.columns([0.95, 0.05])
                
                with col1:
                    # Question header
                    st.subheader(f"Question {idx + 1} of {len(questions)}")
                    
                    # Question type badge
                    badge_color = "🔵" if question.mode == "single" else "🟢"
                    st.markdown(f"{badge_color} **{question.mode.upper()} CHOICE**")
                    
                    # Question text
                    st.markdown(f"**{question.question}**")
                    
                    # Answer options
                    if question.mode == 'single':
                        # Radio buttons for single choice
                        answer = st.radio(
                            "Select your answer:",
                            options=question.choices,
                            key=f"q_{idx}",
                            index=None
                        )
                        st.session_state.user_answers[idx] = answer
                    else:
                        # Multiselect for multiple choice
                        answers = st.multiselect(
                            "Select all correct answers:",
                            options=question.choices,
                            key=f"q_{idx}",
                            default=st.session_state.user_answers.get(idx, [])
                        )
                        st.session_state.user_answers[idx] = answers
                
                with col2:
                    # Tags display
                    st.caption("Tags:")
                    for tag in question.tags:
                        st.caption(f"🏷️ {tag}")
                
                st.markdown("---")

    def submit_and_correct(self):
        """Submit quiz and show correction."""
        if not st.session_state.quiz_generated:
            st.warning("⚠️ Please generate a quiz first!")
            return
        
        if st.session_state.quiz_corrected:
            st.info("Quiz already corrected! Reset to try again.")
            return
        
        # Check if all questions are answered
        questions = st.session_state.questions
        unanswered = []
        
        for idx, question in enumerate(questions):
            answer = st.session_state.user_answers.get(idx)
            if question.mode == 'single':
                if answer is None:
                    unanswered.append(idx + 1)
            else:  # multiple
                if not answer:
                    unanswered.append(idx + 1)
        
        if unanswered:
            st.warning(f"⚠️ Please answer all questions! Unanswered: {', '.join(map(str, unanswered))}")
            return
        
        # Correct the quiz
        corrector = QuizCorrector(questions)
        results = corrector.correct_quiz(st.session_state.user_answers)
        
        st.session_state.results = results
        st.session_state.quiz_corrected = True
        st.rerun()

    def _show_results(self):
        """Display quiz results with visualizations."""
        results = st.session_state.results
        
        # Header
        st.header("📊 Quiz Results")
        
        # Overall score
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Score",
                f"{results['total_score']:.2f} / {results['max_score']}"
            )
        
        with col2:
            st.metric(
                "Percentage",
                f"{results['percentage']:.1f}%"
            )
        
        with col3:
            correct_count = sum(1 for d in results['details'] if d['is_correct'])
            st.metric(
                "Correct Answers",
                f"{correct_count} / {results['max_score']}"
            )
        
        # Performance message
        if results['percentage'] >= 90:
            st.success("🎉 Excellent! Outstanding performance!")
        elif results['percentage'] >= 70:
            st.success("👍 Good job! Well done!")
        elif results['percentage'] >= 50:
            st.warning("📚 Not bad, but there's room for improvement!")
        else:
            st.error("💪 Keep practicing! You'll get better!")
        
        st.markdown("---")
        
        # Visualization
        self._show_visualizations(results)
        
        st.markdown("---")
        
        # Detailed results
        st.subheader("📋 Detailed Results")
        
        for detail in results['details']:
            idx = detail['question_index']
            question = st.session_state.questions[idx]
            
            # Color coding
            if detail['is_correct']:
                status = "✅"
                color = "success"
            else:
                status = "❌"
                color = "error"
            
            with st.expander(f"{status} Question {idx + 1} - Score: {detail['score']:.2f}/1.00"):
                st.markdown(f"**{question.question}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Your Answer(s):**")
                    if question.mode == 'single':
                        st.write(detail['user_answers'] or "No answer")
                    else:
                        st.write(", ".join(detail['user_answers']) if detail['user_answers'] else "No answers")
                
                with col2:
                    st.markdown("**Correct Answer(s):**")
                    st.write(", ".join(detail['correct_answers']))
                
                # Score breakdown for multiple choice
                if question.mode == 'multiple' and not detail['is_correct']:
                    st.caption(f"📊 Partial credit: {detail['score']:.2f} points")

    def _show_visualizations(self, results):
        """Show charts and visualizations."""
        st.subheader("📈 Performance Analysis")
        
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            
            scores = [d['score'] for d in results['details']]
            correct_count = sum(1 for s in scores if s == 1.0)
            partial_count = sum(1 for s in scores if 0 < s < 1.0)
            incorrect_count = sum(1 for s in scores if s == 0)
            
            categories = ['Correct', 'Partial', 'Incorrect']
            counts = [correct_count, partial_count, incorrect_count]
            colors = ['#28a745', '#ffc107', '#dc3545']
            
            ax1.bar(categories, counts, color=colors, alpha=0.7, edgecolor='black')
            ax1.set_ylabel('Number of Questions')
            ax1.set_title('Answer Distribution')
            ax1.set_ylim(0, max(counts) + 2)
            
            # Add count labels on bars
            for i, (cat, count) in enumerate(zip(categories, counts)):
                ax1.text(i, count + 0.1, str(count), ha='center', va='bottom', fontweight='bold')
            
            st.pyplot(fig1)
            plt.close()
        
        with col2:
            # Score per question
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            
            question_nums = [d['question_index'] + 1 for d in results['details']]
            scores = [d['score'] for d in results['details']]
            
            colors_per_q = ['#28a745' if s == 1.0 else '#ffc107' if s > 0 else '#dc3545' for s in scores]
            
            ax2.bar(question_nums, scores, color=colors_per_q, alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Question Number')
            ax2.set_ylabel('Score')
            ax2.set_title('Score per Question')
            ax2.set_ylim(0, 1.1)
            ax2.axhline(y=1.0, color='green', linestyle='--', alpha=0.3, label='Perfect Score')
            ax2.legend()
            
            st.pyplot(fig2)
            plt.close()
        
        # Overall performance pie chart
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        
        percentage = results['percentage']
        remaining = 100 - percentage
        
        colors_pie = ['#28a745', '#e0e0e0']
        explode = (0.05, 0)
        
        ax3.pie([percentage, remaining], 
                labels=['Score', 'Remaining'],
                autopct='%1.1f%%',
                startangle=90,
                colors=colors_pie,
                explode=explode)
        ax3.set_title('Overall Performance')
        
        st.pyplot(fig3)
        plt.close()


# --- STREAMLIT APP ENTRY POINT ---
st.set_page_config(page_title="OOP Quiz Generator", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    h1 {
        color: #1f77b4;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Interactive OOP Quiz Generator")
st.markdown("*Test your knowledge across multiple topics!*")

# Load dataset singleton
dataset = QuestionDataset("quiz_dataset.json")
quiz_view = QuizView(dataset)

# Sidebar controls
with st.sidebar:
    st.title("⚙️ Controls")
    
    # Reset button
    if st.button("🔄 Reset Quiz", use_container_width=True):
        quiz_view.reset_quiz()
    
    st.markdown("---")

# Field selection
selected_fields = quiz_view.select_fields()

# Generate Quiz button
if st.sidebar.button("🎲 Generate Quiz", use_container_width=True, type="primary"):
    quiz_view.generate_quiz(selected_fields)

# Show Quiz
quiz_view.show_quiz()

# Submit & Correct Quiz button
if st.session_state.quiz_generated and not st.session_state.quiz_corrected:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📤 Submit & Correct Quiz", use_container_width=True, type="primary"):
            quiz_view.submit_and_correct()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p></p>
</div>
""", unsafe_allow_html=True)