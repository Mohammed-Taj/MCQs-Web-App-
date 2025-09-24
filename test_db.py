# test_db_full.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# --- Flask & SQLAlchemy Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://localhost/QuizDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(10))  # admin or student

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    questions = db.relationship('Question', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    text = db.Column(db.String(300))
    choice_a = db.Column(db.String(100))
    choice_b = db.Column(db.String(100))
    choice_c = db.Column(db.String(100))
    choice_d = db.Column(db.String(100))
    correct = db.Column(db.String(1))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)
    
    student = db.relationship('User', backref='results')
    quiz = db.relationship('Quiz', backref='results')

# --- Initialize DB & Insert Defaults ---
with app.app_context():
    db.create_all()
    print("✅ All tables created successfully.")

    # Add default admin
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin', role='admin')
        db.session.add(admin)
        print("✅ Default admin added.")

    # Add default student
    if not User.query.filter_by(username='student').first():
        student = User(username='student', password='student', role='student')
        db.session.add(student)
        print("✅ Default student added.")

    db.session.commit()

    # Add sample quiz
    if not Quiz.query.filter_by(title='Sample Quiz').first():
        quiz = Quiz(title='Sample Quiz', description='This is a test quiz.')
        db.session.add(quiz)
        db.session.commit()
        print("✅ Sample quiz added.")

        # Add sample question
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
        print("✅ Sample question added.")

# --- Simulate Student Taking the Quiz ---
with app.app_context():
    student = User.query.filter_by(username='student').first()
    quiz = Quiz.query.filter_by(title='Sample Quiz').first()

    # Check if result already exists
    existing_result = Result.query.filter_by(student_id=student.id, quiz_id=quiz.id).first()
    if not existing_result:
        score = 0
        for q in quiz.questions:
            # Student answers 'A' for testing
            answer = 'A'
            if answer == q.correct:
                score += 1

        result = Result(student_id=student.id, quiz_id=quiz.id, score=score, total=len(quiz.questions))
        db.session.add(result)
        db.session.commit()
        print(f"Student {student.username} completed '{quiz.title}' with score {score}/{len(quiz.questions)}")
    else:
        print(f"Student {student.username} already has a result for '{quiz.title}'.")

# --- Display Results ---
with app.app_context():
    student = User.query.filter_by(username='student').first()
    results = student.results

    print(f"\nResults for {student.username}:")
    for r in results:
        print(f"- Quiz: {r.quiz.title}, Score: {r.score}/{r.total}")
# with app.app_context():
#     # Delete all results first (due to foreign key constraints)
#     deleted_results = Result.query.delete()
#     db.session.commit()
#     print(f"✅ Deleted {deleted_results} result records.")

#     # Delete all questions
#     deleted_questions = Question.query.delete()
#     db.session.commit()
#     print(f"✅ Deleted {deleted_questions} question records.")

#     # Delete all quizzes
#     deleted_quizzes = Quiz.query.delete()
#     db.session.commit()
#     print(f"✅ Deleted {deleted_quizzes} quiz records.")

#     # Delete all users
#     deleted_users = User.query.delete()
#     db.session.commit()
#     print(f"✅ Deleted {deleted_users} user records.")