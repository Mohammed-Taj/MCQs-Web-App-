from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from models import Question, Result, db, User, Quiz
from db_utils import (
    add_question, add_quiz, delete_question, delete_quiz, update_question, update_quiz, add_result
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc://localhost/QuizDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'change-this-secret'
db.init_app(app)

# --- Home Route ---
@app.route('/')
def home():
    if 'role' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'student':
            return redirect(url_for('student_dashboard'))
    return render_template('home.html')


# --- Register Route ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'student')

        if not username or not password:
            flash('⚠️ Username and password are required!')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('⚠️ User already exists!')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, role="student", is_active=True)
        db.session.add(new_user)
        db.session.commit()
        flash(f'✅ User {username} created successfully as {role}!')
        return redirect(url_for('login'))

    return render_template('register.html')


# --- Login Route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash("⚠️ Your account is inactive. Contact the admin.")
                return redirect(url_for('login'))

            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            flash(f'✅ Login successful! Welcome {user.username} ({user.role})')

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))

        else:
            flash('❌ Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')


# --- Logout Route ---
@app.route('/logout')
def logout():
    session.clear()
    flash('✅ Logged out successfully.')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        flash('Please login first!')
        return redirect(url_for('login'))

    if session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif session['role'] == 'student':
        return redirect(url_for('student_dashboard'))
    else:
        flash('Unknown role!')
        return redirect(url_for('login'))

# ------------------ Admin Routes ------------------

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Access denied!')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


@app.route('/admin')
@admin_required
def admin_dashboard():
    # --- Dashboard Stats ---
    total_users = User.query.count()
    total_active = User.query.filter_by(is_active=True).count()
    total_quizzes = Quiz.query.count()
    total_questions = Question.query.count()

    # --- User Management ---
    users = User.query.all()
    
    # --- Quiz List ---
    quizzes = Quiz.query.all()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_active=total_active,
                           total_quizzes=total_quizzes,
                           total_questions=total_questions,
                           users=users,
                           quizzes=quizzes)

@app.route('/admin/add_quiz', methods=['GET', 'POST'])
@admin_required
def add_quiz_route():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        quiz = add_quiz(title, description)
        if quiz:
            flash('Quiz added successfully!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Quiz with this title already exists.')
    return render_template('add_quiz.html')


@app.route('/admin/update_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def update_quiz_route(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        new_title = request.form.get('title')
        new_description = request.form.get('description')
        update_quiz(quiz_id, new_title, new_description)
        flash('Quiz updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('update_quiz.html', quiz=quiz)


@app.route('/admin/delete_quiz/<int:quiz_id>', methods=['POST'])
@admin_required
def delete_quiz_route(quiz_id):
    if delete_quiz(quiz_id):
        flash('Quiz deleted successfully!')
    else:
        flash('Quiz not found.')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/<int:quiz_id>/add_question', methods=['GET', 'POST'])
@admin_required
def add_question_route(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        question = add_question(
            quiz_id,
            request.form.get('text'),
            request.form.get('choice_a'),
            request.form.get('choice_b'),
            request.form.get('choice_c'),
            request.form.get('choice_d'),
            request.form.get('correct')
        )
        if question:
            flash('Question added successfully!')
            return redirect(url_for('update_quiz_route', quiz_id=quiz_id))
        else:
            flash('Failed to add question.')
    return render_template('add_question.html', quiz=quiz)


@app.route('/admin/update_question/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def update_question_route(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        update_question(
            question_id,
            new_text=request.form.get('text'),
            choice_a=request.form.get('choice_a'),
            choice_b=request.form.get('choice_b'),
            choice_c=request.form.get('choice_c'),
            choice_d=request.form.get('choice_d'),
            correct=request.form.get('correct')
        )
        flash('Question updated successfully!')
        return redirect(url_for('update_quiz_route', quiz_id=question.quiz_id))
    return render_template('update_question.html', question=question)


@app.route('/admin/delete_question/<int:question_id>', methods=['POST'])
@admin_required
def delete_question_route(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    delete_question(question_id)
    flash('Question deleted successfully!')
    return redirect(url_for('update_quiz_route', quiz_id=quiz_id))

@app.route('/admin/update_user/<int:user_id>', methods=['POST'])
@admin_required
def update_user_route(user_id):
    user = User.query.get_or_404(user_id)
    user.role = request.form.get('role')
    user.is_active = request.form.get('is_active') == '1'
    db.session.commit()
    flash('✅ User updated successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/analysis')
@admin_required
def analysis():
    quizzes = Quiz.query.all()
    results = Result.query.order_by(Result.timestamp.desc()).all()

    # --- Prepare chart data: average score per quiz ---
    chart_labels = [q.title for q in quizzes]
    chart_data = []
    for q in quizzes:
        if q.results:
            avg = sum((r.score / r.total * 100) for r in q.results if r.total > 0) / len(q.results)
        else:
            avg = 0
        chart_data.append(round(avg, 2))

    total_quizzes = len(quizzes)
    total_students = User.query.filter_by(role='student').count()
    total_results = len(results)
    total_questions = Question.query.count()

    # --- Performance summary ---
    excellent_count = 0
    good_count = 0
    poor_count = 0
    average_score = 0

    if total_results > 0:
        total_percentage = 0
        for r in results:
            pct = (r.score / r.total * 100) if r.total > 0 else 0
            total_percentage += pct
            if pct >= 80:
                excellent_count += 1
            elif pct >= 50:
                good_count += 1
            else:
                poor_count += 1
        average_score = total_percentage / total_results / 100  # normalized 0-1 for template

    return render_template('analysis.html',
                           results=results,
                           chart_labels=chart_labels,
                           chart_data=chart_data,
                           total_quizzes=total_quizzes,
                           total_students=total_students,
                           total_results=total_results,
                           total_questions=total_questions,
                           excellent_count=excellent_count,
                           good_count=good_count,
                           poor_count=poor_count,
                           average_score=average_score,
                           quiz_list=quizzes)


# ------------------ Student Routes ------------------

def student_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'role' not in session or session['role'] != 'student':
            flash('Access denied!')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student = User.query.get(session['user_id'])  # or session.get('user_id')
    quizzes = Quiz.query.all()
    
    # Calculate total attempts and average score per quiz for the student
    attempts_per_quiz = {}
    avg_score_per_quiz = {}
    
    for quiz in quizzes:
        user_results = [r for r in quiz.results if r.student_id == student.id]
        attempts_per_quiz[quiz.id] = len(user_results)
        if user_results:
            total_score = sum(r.score for r in user_results)
            total_possible = sum(r.total for r in user_results)
            avg_score_per_quiz[quiz.id] = round(total_score / total_possible * 100, 1)
        else:
            avg_score_per_quiz[quiz.id] = 0
    
    # Overall average score across all attempts
    all_results = student.results
    if all_results:
        total_score = sum(r.score for r in all_results)
        total_possible = sum(r.total for r in all_results)
        overall_avg = round(total_score / total_possible * 100, 1)
    else:
        overall_avg = 0
    total_attempts = sum(attempts_per_quiz.values())
    return render_template(
        'student_dashboard.html',
        quizzes=quizzes,
        attempts_per_quiz=attempts_per_quiz,
        avg_score_per_quiz=avg_score_per_quiz,
        overall_avg=overall_avg,
        total_attempts = total_attempts
    )



@app.route('/student/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@student_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    student = User.query.get(session['user_id'])

    if request.method == 'POST':
        score = 0
        student_answers = {}  # store answers temporarily

        for q in quiz.questions:
            answer = request.form.get(str(q.id))
            student_answers[q.id] = answer  # keep user's answer for review
            print("DEBUG:", q.id, "| Correct:", q.correct, "| Answer:", answer)
            if answer and answer.strip().upper() == q.correct.strip().upper():
                score += 1

        # Optionally save result in DB
        add_result(student.id, quiz.id, score, len(quiz.questions))

        flash(f'Quiz completed! Your score: {score}/{len(quiz.questions)}')
        # Instead of redirecting, render review page immediately
        return render_template(
            'review_quiz.html',
            quiz=quiz,
            student_answers=student_answers,
            score=score,
            total=len(quiz.questions)
        )

    return render_template('take_quiz.html', quiz=quiz)



@app.route('/student/results')
@student_required
def student_results():
    student = db.session.get(User, session['user_id'])  # use Session.get() to avoid SQLAlchemy warning
    results = list(student.results)  # convert generator to list

    total_results = len(results)
    excellent_count = 0
    good_count = 0
    poor_count = 0
    average_score = 0

    if total_results > 0:
        total_percentage = 0
        for r in results:
            pct = (r.score / r.total * 100) if r.total > 0 else 0
            total_percentage += pct
            if pct >= 80:
                excellent_count += 1
            elif pct >= 60:
                good_count += 1
            else:
                poor_count += 1
        average_score = total_percentage / total_results / 100  # normalized 0-1

    # List of unique quiz titles
    unique_quiz_titles = list({r.quiz.title for r in results})

    return render_template(
        'student_results.html',
        results=results,
        total_results=total_results,
        excellent_count=excellent_count,
        good_count=good_count,
        poor_count=poor_count,
        average_score=average_score,
        unique_quizzes=len(unique_quiz_titles)
    )


@app.route('/student/update_profile', methods=['GET', 'POST'])
@student_required
def update_profile():
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')

        if not new_username:
            flash("⚠️ Username cannot be empty.")
            return redirect(url_for('update_profile'))

        # Check if username is taken by another user
        existing_user = User.query.filter(User.username == new_username, User.id != user.id).first()
        if existing_user:
            flash("⚠️ Username already taken.")
            return redirect(url_for('update_profile'))

        user.username = new_username

        # Update password only if provided
        if new_password:
            user.password = generate_password_hash(new_password)

        db.session.commit()
        flash("✅ Profile updated successfully!")
        return redirect(url_for('student_dashboard'))

    return render_template('update_profile.html', user=user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
