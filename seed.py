from app import app
from models import db
from db_utils import create_user, add_quiz, Question

with app.app_context():
    # Create default users
    create_user('admin', 'admin', 'admin')
    create_user('student', 'student', 'student')

    # Create sample quiz
    quiz = add_quiz('Sample Quiz', 'This is a test quiz.')
    if quiz:
        q1 = Question(
            quiz_id=quiz.id,
            text="What is 2 + 2?",
            choice_a="3",
            choice_b="4",
            choice_c="5",
            choice_d="6",
            correct="B"
        )
        db.session.add(q1)
        db.session.commit()
