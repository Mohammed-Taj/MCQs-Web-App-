from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(10))  # admin or student
    is_active = db.Column(db.Boolean, default=True) 

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(200))
    description = db.Column(db.UnicodeText)
    questions = db.relationship('Question', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    text = db.Column(db.UnicodeText)
    choice_a = db.Column(db.Unicode(300))
    choice_b = db.Column(db.Unicode(300))
    choice_c = db.Column(db.Unicode(300))
    choice_d = db.Column(db.Unicode(300))
    correct = db.Column(db.String(1))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # ← new column with default

    student = db.relationship('User', backref='results')
    quiz = db.relationship('Quiz', backref='results')