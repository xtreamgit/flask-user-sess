from flask import Flask, session, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'supersecretkey'


# -----------Configure Flask-Session ----------
# Set the session cookie name
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'my_custom_session_cookie'

# Initialize Flask-Session
Session(app)
#----------------------------------------------

# // LoginManager is a class provided by the Flask-Login extension.
# // By calling LoginManager(), you create a new instance of the LoginManager class.

# Creating an Instance of LoginManager
login_manager = LoginManager() 

# Initializes the LoginManager for use with the given Flask app.
login_manager.init_app(app) 

# Set the login view (the endpoint to redirect to when a user needs to log in)
login_manager.login_view = 'login'

# Customize the message flashed to users when they are redirected to the login view
login_manager.login_message = "Please log in to access the exam."
login_manager.login_message_category = "info"

# User Class Initialization
class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        # In a real application, this method would query the database
        if user_id == "user1":
            return User(user_id)
        return None

# Register the user loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Route for the root index page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(request.form['username'])
        login_user(user)
        return redirect(url_for('protected'))
    return render_template('login.html')

@app.route('/protected')
@login_required
def protected():
    return f'Logged in as: {current_user.id}'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out'

# ********** Session Code

@app.route('/set_session')
def set_session():
    session['username'] = 'user1'
    return 'Session set'

@app.route('/get_session')
def get_session():
    username = session.get('username')
    return f'Logged in as {username}'

if __name__ == '__main__':
    app.run(debug=True)
