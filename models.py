import json
import random

class Question:
    """
    Represents a single quiz question.
    - question: The question text.
    - choices: List of possible answers.
    - correct: List of correct answers.
    - mode: 'single' or 'multiple'.
    - tags: List of fields/tags for filtering.
    """
    def __init__(self, question, choices, correct, mode, tags):
        self.question = question
        self.choices = choices
        self.correct = correct
        self.mode = mode
        self.tags = tags
    
    def is_correct(self, selected_answers):
        """Check if the selected answers are correct."""
        if self.mode == 'single':
            return selected_answers == self.correct[0] if selected_answers else False
        else:  # multiple
            return set(selected_answers) == set(self.correct)
    
    def calculate_score(self, selected_answers):
        """
        Calculate score for the question.
        Single choice: 1 if correct, 0 otherwise
        Multiple choice: proportional score
        """
        if self.mode == 'single':
            return 1.0 if self.is_correct(selected_answers) else 0.0
        else:
            if not selected_answers:
                return 0.0
            
            selected_set = set(selected_answers)
            correct_set = set(self.correct)
            
            # Calculate: (|correct ∩ selected| / |correct|) - (|selected - correct| / |correct|)
            correct_selected = len(selected_set & correct_set)
            incorrect_selected = len(selected_set - correct_set)
            
            score = (correct_selected / len(correct_set)) - (incorrect_selected / len(correct_set))
            return max(0.0, score)
    
    def __repr__(self):
        return f"Question(question='{self.question[:30]}...', mode='{self.mode}', tags={self.tags})"


class QuestionDataset:
    """
    Singleton class to load quiz questions from a JSON file.
    - Loads all questions as Question objects.
    - Provides a method to get all unique tags for filtering.
    """
    _instance = None
    _questions = []
    _all_tags = set()

    def __new__(cls, filepath=None):
        if cls._instance is None:
            cls._instance = super(QuestionDataset, cls).__new__(cls)
            if filepath:
                cls._instance._load_questions(filepath)
        return cls._instance

    def _load_questions(self, filepath):
        """Load questions from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._questions = []
            for item in data:
                question = Question(
                    question=item['question'],
                    choices=item['choices'],
                    correct=item['correct'],
                    mode=item['mode'],
                    tags=item['tags']
                )
                self._questions.append(question)
                self._all_tags.update(item['tags'])
            
            print(f"✓ Loaded {len(self._questions)} questions with {len(self._all_tags)} unique tags")
        except Exception as e:
            print(f"✗ Error loading questions: {e}")
            self._questions = []
            self._all_tags = set()
    
    def get_all_questions(self):
        """Return all loaded questions."""
        return self._questions
    
    def get_all_tags(self):
        """Return all unique tags."""
        return sorted(list(self._all_tags))
    
    def get_questions_by_tags(self, tags):
        """Filter questions by tags (OR logic)."""
        if not tags:
            return self._questions
        
        filtered = []
        for q in self._questions:
            if any(tag in q.tags for tag in tags):
                filtered.append(q)
        return filtered


class QuizGenerator:
    """
    Generates a quiz from a dataset filtered by fields/tags.
    """
    def __init__(self, dataset):
        self.dataset = dataset
    
    def generate_quiz(self, selected_tags=None, num_questions=10):
        """
        Generate a random quiz with the specified number of questions.
        
        Args:
            selected_tags: List of tags to filter questions
            num_questions: Number of questions to include in the quiz
        
        Returns:
            List of Question objects
        """
        # Get filtered questions
        if selected_tags:
            available_questions = self.dataset.get_questions_by_tags(selected_tags)
        else:
            available_questions = self.dataset.get_all_questions()
        
        if not available_questions:
            return []
        
        # Randomly select questions
        num_to_select = min(num_questions, len(available_questions))
        selected_questions = random.sample(available_questions, num_to_select)
        
        return selected_questions


class QuizCorrector:
    """
    Corrects a quiz and calculates scores.
    """
    def __init__(self, questions):
        self.questions = questions
    
    def correct_quiz(self, user_answers):
        """
        Correct the quiz based on user answers.
        
        Args:
            user_answers: Dictionary mapping question index to selected answer(s)
        
        Returns:
            Dictionary with results including scores, total, and details
        """
        results = {
            'total_score': 0.0,
            'max_score': len(self.questions),
            'percentage': 0.0,
            'details': []
        }
        
        for idx, question in enumerate(self.questions):
            selected = user_answers.get(idx, [] if question.mode == 'multiple' else None)
            
            # Calculate score for this question
            score = question.calculate_score(selected)
            is_correct = question.is_correct(selected)
            
            detail = {
                'question_index': idx,
                'question_text': question.question,
                'mode': question.mode,
                'correct_answers': question.correct,
                'user_answers': selected,
                'score': score,
                'is_correct': is_correct
            }
            
            results['details'].append(detail)
            results['total_score'] += score
        
        # Calculate percentage
        if results['max_score'] > 0:
            results['percentage'] = (results['total_score'] / results['max_score']) * 100
        
        return results