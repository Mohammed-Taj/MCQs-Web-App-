from docx import Document
from db_utils import add_quiz, add_question
from app import app  # your Flask app

# Correct answers in order
correct_answers = ['b','b','b','b','a',
                   'b','c','b','b','d',
                   'b','c','a','b','a',
                   'b','b','b','b','b',
                   'a','b','b','a','b',
                   'b','b','b','a', 'a',
                   'b','b','b','a','b',
                   'c','b','a','b','b']

def import_quiz_from_word(file_path):
    doc = Document(file_path)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    quiz_title = lines[0]
    quiz_description = "Auto-imported quiz Lec 4."

    with app.app_context():
        quiz = add_quiz(quiz_title, quiz_description)

        q_number = 0
        i = 1
        while i < len(lines):
            line = lines[i]
            # Detect question line (starts with number + dot)
            if line[0].isdigit() and '.' in line:
                question_text = line.split('.', 1)[1].strip()
                choices = {}
                choice_count = 0
                j = i + 1
                # Collect 4 choices dynamically
                while choice_count < 4 and j < len(lines):
                    cline = lines[j]
                    if cline and cline[0].lower() in ['a','b','c','d']:
                        choice_key = cline[0].upper()
                        choice_text = cline[2:].strip() if len(cline) > 2 else ""
                        choices[choice_key] = choice_text
                        choice_count += 1
                    j += 1

                # Add question to DB
                correct = correct_answers[q_number].upper()
                add_question(
                    quiz.id,
                    question_text,
                    choices.get("A"),
                    choices.get("B"),
                    choices.get("C"),
                    choices.get("D"),
                    correct
                )

                q_number += 1
                i = j  # move to next question
            else:
                i += 1

        print(f"Quiz '{quiz_title}' imported successfully with {q_number} questions!")

# ✅ Run inside Flask app context
with app.app_context():
    import_quiz_from_word("Linear_Regression_MLR_40MCQs final - Copy.docx")
