from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'pca-user-session'

Session(app)

# MongoDB connections
client = MongoClient('mongodb://localhost:27017/')
db_exam = client['examDB']
questions_collection = db_exam['questions']
db_user = client['user_database']
user_collection = db_user['user_info']

# Create an instance of LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Define a simple User class with Flask-Login's UserMixin
class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        user = user_collection.find_one({"username": user_id})
        if user:
            return User(user_id)
        return None

    @staticmethod
    def register(user_id, password):
        if user_collection.find_one({"username": user_id}):
            return False
        hashed_password = generate_password_hash(password)
        user_collection.insert_one({"username": user_id, "password": hashed_password})
        return True

    @staticmethod
    def verify_password(user_id, password):
        user = user_collection.find_one({"username": user_id})
        if user and check_password_hash(user['password'], password):
            return True
        return False

# Register the user loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']
        if not re.match(r"^[a-zA-Z0-9]{8,}$", password):
            flash("Password must be at least 8 alphanumeric characters.", "danger")
        elif User.register(user_id, password):
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Username already exists.", "danger")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']
        if User.verify_password(user_id, password):
            user = User(user_id)
            login_user(user)
            return redirect(url_for('protected'))
        flash("Invalid username or password.", "danger")
    return render_template('login.html')

@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html', session_id=session.sid, username=current_user.id)

@app.route('/dbvalues')
@login_required
def dbvalues():
    user_data = user_collection.find_one({"username": current_user.id})
    return render_template('dbvalues.html', session_id=session.sid, username=current_user.id, password_hash=user_data['password'])

@app.route('/question/<int:question_number>')
@login_required
def display_question(question_number):
    try:
        question_data = questions_collection.find_one({'number': question_number})
        if not question_data:
            return "Question not found", 404
        return render_template('question.html', question=question_data)
    except Exception as e:
        return f"An error occurred while connecting to the database: {str(e)}", 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
