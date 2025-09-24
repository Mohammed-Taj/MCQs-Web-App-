from datetime import datetime
from models import db, User, Quiz, Question, Result

# --- User Operations ---
def create_user(username, password, role):
    if not User.query.filter_by(username=username).first():
        user = User(username=username, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return user
    return None

def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False

def update_user(username, new_username=None, new_password=None, new_role=None):
    user = User.query.filter_by(username=username).first()
    if user:
        if new_username:
            user.username = new_username
        if new_password:
            user.password = new_password
        if new_role:
            user.role = new_role
        db.session.commit()
        return user
    return None


# --- Quiz Operations ---
def add_quiz(title, description):
    if not Quiz.query.filter_by(title=title).first():
        quiz = Quiz(title=title, description=description)
        db.session.add(quiz)
        db.session.commit()
        return quiz
    return None

def update_quiz(quiz_id, new_title=None, new_description=None):
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        if new_title:
            quiz.title = new_title
        if new_description:
            quiz.description = new_description
        db.session.commit()
        return quiz
    return None

def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        # Optional: delete related questions and results
        for q in quiz.questions:
            db.session.delete(q)
        for r in quiz.results:
            db.session.delete(r)
        db.session.delete(quiz)
        db.session.commit()
        return True
    return False
# --- Question Operations ---
def add_question(quiz_id, text, choice_a, choice_b, choice_c, choice_d, correct):
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        question = Question(
            quiz_id=quiz_id,
            text=text,
            choice_a=choice_a,
            choice_b=choice_b,
            choice_c=choice_c,
            choice_d=choice_d,
            correct=correct.upper()  # Ensure correct is uppercase
        )
        db.session.add(question)
        db.session.commit()
        return question
    return None

def update_question(question_id, new_text=None, choice_a=None, choice_b=None, choice_c=None, choice_d=None, correct=None):
    question = Question.query.get(question_id)
    if question:
        if new_text:
            question.text = new_text
        if choice_a:
            question.choice_a = choice_a
        if choice_b:
            question.choice_b = choice_b
        if choice_c:
            question.choice_c = choice_c
        if choice_d:
            question.choice_d = choice_d
        if correct:
            question.correct = correct.upper()
        db.session.commit()
        return question
    return None

def delete_question(question_id):
    question = Question.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
        return True
    return False
# --- Result Operations ---
def add_result(student_id, quiz_id, score, total):
    result = Result(
        student_id=student_id,
        quiz_id=quiz_id,
        score=score,
        total=total,
        timestamp=datetime.utcnow()  # ← explicitly set timestamp
    )
    db.session.add(result)
    db.session.commit()
    return result


def update_result(result_id, score=None, total=None):
    result = Result.query.get(result_id)
    if result:
        if score is not None:
            result.score = score
        if total is not None:
            result.total = total
        db.session.commit()
        return result
    return None

def delete_result(result_id):
    result = Result.query.get(result_id)
    if result:
        db.session.delete(result)
        db.session.commit()
        return True
    return False

def get_student_results(student_id):
    student = User.query.get(student_id)
    if student:
        return student.results
    return []
