# OOP Quiz Generator - Solution Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Implementation Details](#implementation-details)
4. [Usage Guide](#usage-guide)

---

## 🎯 Overview

This project implements an **interactive quiz application** using Object-Oriented Programming (OOP) principles and Streamlit. The application allows users to:
- Select topics/tags to filter questions
- Generate randomized quizzes
- Answer single-choice and multiple-choice questions
- Get instant feedback with detailed scoring
- View performance analytics with visualizations

---

## 🏗️ Architecture

### Class Diagram
![Alt text](<Untitled diagram-2025-10-26-174032.png>)

## 🔧 Implementation Details

### 1. Question Class

**Purpose**: Represents a single quiz question with all its attributes.

**Key Methods**:
- `is_correct(selected_answers)`: Validates if the answer is completely correct
- `calculate_score(selected_answers)`: Calculates the score using the formula:

For **multiple choice**:
```
score = max(0, (|correct ∩ selected| / |correct|) - (|selected - correct| / |correct|))
```

**Example**:
```python
# Question with 3 correct answers: ["A", "B", "C"]
# User selects: ["A", "B", "D"]

correct_selected = 2  # A and B
incorrect_selected = 1  # D
total_correct = 3

score = (2/3) - (1/3) = 0.33
```

### 2. QuestionDataset Class (Singleton Pattern)

**Purpose**: Ensures only one instance loads the questions from JSON.

**Why Singleton?**
- Avoids loading the same dataset multiple times
- Saves memory and improves performance
- Provides a global access point

**Implementation**:
```python
def __new__(cls, filepath=None):
    if cls._instance is None:
        cls._instance = super(QuestionDataset, cls).__new__(cls)
        if filepath:
            cls._instance._load_questions(filepath)
    return cls._instance
```

### 3. QuizGenerator Class

**Purpose**: Creates randomized quizzes based on selected topics.

**Logic**:
1. Filter questions by tags (OR logic)
2. Randomly sample N questions
3. Return the selected questions

**Tag Filtering**:
- If no tags selected → all questions available
- If tags selected → questions matching ANY tag (OR logic)

### 4. QuizCorrector Class

**Purpose**: Evaluates user answers and calculates detailed scores.

**Output Structure**:
```python
{
    'total_score': 7.5,
    'max_score': 10,
    'percentage': 75.0,
    'details': [
        {
            'question_index': 0,
            'question_text': "...",
            'mode': 'single',
            'correct_answers': [...],
            'user_answers': [...],
            'score': 1.0,
            'is_correct': True
        },
        ...
    ]
}
```

### 5. QuizView Class

**Purpose**: Handles all Streamlit UI rendering and interactions.

**Session State Management**:
```python
st.session_state.quiz_generated     # Quiz created?
st.session_state.questions          # Current questions
st.session_state.user_answers       # User's selections
st.session_state.quiz_corrected     # Quiz submitted?
st.session_state.results            # Correction results
```

**UI Flow**:
1. **Configuration** → Select topics + number of questions
2. **Generation** → Create randomized quiz
3. **Answering** → Display questions with appropriate widgets
4. **Submission** → Validate and correct answers
5. **Results** → Show scores + visualizations

---


## 📖 Usage Guide

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the application**:
```bash
streamlit run app.py
```

### Step-by-Step Usage

#### Step 1: Configure Your Quiz
![Alt text](<Capture d’écran (890).png>)

In the sidebar:
- Select one or more topics (math, physics, programming, etc.)
- Choose the number of questions (5-50)
- Click "🎲 Generate Quiz"

![Alt text](<Capture d’écran (891).png>)

#### Step 2: Answer Questions
![Alt text](<Capture d’écran (892).png>)

- **Single choice**: Select one answer using radio buttons
- **Multiple choice**: Select all correct answers using checkboxes
- Questions are numbered and show their tags

![Alt text](<Capture d’écran (893).png>)

#### Step 3: Submit and Review
![Alt text](<Capture d’écran (894).png>)
![Alt text](<Capture d’écran (895).png>)
![Alt text](<Capture d’écran (896).png>)
![Alt text](<Capture d’écran (897).png>)
- Click "📤 Submit & Correct Quiz"
- View your total score and percentage
- See which questions were correct/incorrect
- Analyze performance with charts
- Review correct answers for missed questions

#### Step 4: Try Again
- Click "🔄 Reset Quiz" in the sidebar
- Configure a new quiz with different topics

---


## 🧮 Scoring Algorithm Explained

### Single Choice Questions
Simple binary scoring:
- **Correct answer**: 1.0 point
- **Wrong answer**: 0.0 points
- **No answer**: 0.0 points

### Multiple Choice Questions
Proportional scoring with penalty for wrong selections:

**Formula**:
```
score = max(0, (correct_selected / total_correct) - (wrong_selected / total_correct))
```

**Examples**:

#### Example 1: Perfect Answer
```
Correct answers: [A, B, C]
User selects: [A, B, C]

correct_selected = 3
wrong_selected = 0
total_correct = 3

score = (3/3) - (0/3) = 1.0 - 0.0 = 1.0 ✅
```

#### Example 2: Partial Credit
```
Correct answers: [A, B, C]
User selects: [A, B]

correct_selected = 2
wrong_selected = 0
total_correct = 3

score = (2/3) - (0/3) = 0.67 - 0.0 = 0.67 📊
```

#### Example 3: Mixed Answer
```
Correct answers: [A, B, C]
User selects: [A, B, D]

correct_selected = 2 (A and B)
wrong_selected = 1 (D)
total_correct = 3

score = (2/3) - (1/3) = 0.67 - 0.33 = 0.33 📊
```

#### Example 4: Penalty Below Zero
```
Correct answers: [A, B]
User selects: [C, D, E]

correct_selected = 0
wrong_selected = 3
total_correct = 2

score = (0/2) - (3/2) = 0.0 - 1.5 = -1.5
score = max(0, -1.5) = 0.0 ❌
```

**Why This Formula?**
- Rewards partial knowledge
- Penalizes guessing randomly
- Prevents gaming the system by selecting all options
- Fair assessment of understanding

---


## 📈 Performance Metrics

### Grading Scale
- **90-100%**: 🎉 Excellent! Outstanding performance!
- **70-89%**: 👍 Good job! Well done!
- **50-69%**: 📚 Not bad, but there's room for improvement!
- **0-49%**: 💪 Keep practicing! You'll get better!

### Visualizations Provided

1. **Answer Distribution Bar Chart**
   - Shows count of Correct, Partial, and Incorrect answers
   - Quick overview of overall performance

2. **Score Per Question Bar Chart**
   - Individual score for each question
   - Color-coded by performance
   - Helps identify difficult questions

3. **Overall Performance Pie Chart**
   - Visual representation of score percentage
   - Shows achieved vs remaining points

---

## 📦 File Structure

```
quiz-app/
│
├── app.py                  # Main Streamlit application
├── models.py               # OOP classes (Question, Dataset, etc.)
├── quiz_dataset.json       # Question database
├── requirements.txt        # Python dependencies
├── README.md              # Project overview
└── Readme-Solution.md     # This file (detailed solution)
```

---
