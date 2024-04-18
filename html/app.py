# pylint: skip-file
"""
Flask Application for File Upload and Management

This application allows users to upload files, manage file queues, and approve uploaded files. 
It includes user authentication via GitHub OAuth, file upload with validation, and an management dashboard 
for managing user files and approvals.

Routes:
    - /login: Initiates GitHub OAuth authentication flow.
    - /auth: Handles OAuth callback and user authentication.
    - /logout: Logs out the user.
    - /: Displays the index page with uploaded images.
    - /dashboard: Displays the user's dashboard with uploaded and queued images.
    - /upload: Handles file upload with validation and redirects to upload result.
    - /upload/result: Displays the result of the file upload.
    - /upload/approve: Approves the uploaded file.
    - /delete_image: Deletes an uploaded image.
    - /management/users: Displays the management page for users.
    - /management/approve: management approval page for queued images.
    - /faq: Displays the frequently asked questions page.
    - Error Handlers: Handles 404 and 405 errors with custom error pages.

Environment Variables:
    - DATABASE_NAME: SQLite database file path.
    - FLASK_SECRET_KEY: Secret key for Flask session management.
    - GITHUB_CLIENT_ID: GitHub OAuth client ID.
    - GITHUB_CLIENT_SECRET: GitHub OAuth client secret.

Dependencies:
    - flask: Flask web framework.
    - authlib: Library for OAuth authentication.
    - dotenv: Library for loading environment variables from .env file.
    - filehandler: Custom module for file handling functions.
    - queuehandler: Custom module for managing file queues.
    - db_models: Module containing database models.
    - db_user_helper: Module for database user operations.
    - user_roles: Module for defining user roles.

Usage:
    - Install dependencies with `pip install -r requirements.txt`.
    - Set up environment variables in a .env file.
    - Run the application with `python app.py`.

Author:
    Inflac
"""

import os

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from authlib.integrations.flask_client import OAuth
#from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
from functools import wraps

from filehandler import sanitize_file, safe_file, delete_file, get_all_images_for_all_users
from queuehandler import approve_file
from db_models import db, create_roles
from db_user_helper import add_user_to_users, get_user_from_users, get_users_data_for_dashboard
from helper import logging, sanitize_string

from role_based_access import check_access

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.environ.get('DATABASE_NAME')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)
# Create the database tables
with app.app_context():
    db.create_all()
    create_roles()

app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['QUEUE_FOLDER'] = 'static/queue'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.environ.get('GITHUB_CLIENT_ID'),
    client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'user:email'},
)

def login_required(view):
    """
    Decorator function to protect routes that require authentication.
    Redirects unauthenticated users to the login page.
    """
    @wraps(view)
    def decorated_view(*args, **kwargs):
        if 'token' not in session:
            # Redirect to the login route if the user is not authenticated
            return redirect(url_for('login', next=request.url))

        user = get_user_from_users(session['user_name'])
        if not user:
            return redirect(url_for('index'))

        session['user_role'] = user.role.id
        return view(*args, **kwargs)
    return decorated_view

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = github.authorize_access_token()
    if not token:
        return "Login failed."

    session['token'] = token
    user = github.get('https://api.github.com/user', token=token)
    if not user.ok:
        return "Failed to fetch user data from GitHub."

    user_data = user.json()
    session['user_data'] = user_data
    session['user_name'] = user_data['login']

    user = get_user_from_users(user_data['login'])
    if user:
        session['user_role'] = user.role.id
        return redirect(url_for('dashboard'))

    if add_user_to_users(user_data['login']):
        return redirect(url_for('dashboard'))
    return "User couldn't be added to the database"


@app.route('/logout')
def logout():
    if session.get('token'):
        session.clear()
        return render_template('logout.html')
    else:
        return "Stop making weird requests"

@app.route('/')
def index():
    uploaded_images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', uploaded_images=uploaded_images)

@app.route('/dashboard')
@login_required
def dashboard():
    # Clear session data related to uploaded file
    session.pop('uploaded_file', None)

    user = get_user_from_users(session['user_name'])
    if not user:
        return redirect(url_for('login'))

    # Get list of uploaded images
    queued_images = user.get_user_files_queue()
    uploaded_images = user.get_user_files_uploads()

    return render_template('dashboard.html', uploaded_images=uploaded_images,
        queued_images=queued_images)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if request.method != 'POST':
        return redirect(url_for('index'))

    if not check_access(session['user_name'], 1):
        return render_template('error/blocked.html', support_url=os.environ.get('SUPPORT_URL'))

    file = request.files['file']
    if not file:
        return redirect(url_for('index'))

    file = sanitize_file(file, app.config['MAX_CONTENT_LENGTH'])
    if file != False:        
        if safe_file(file,app.config['QUEUE_FOLDER'], session['user_name']):
            # Store the filename in the session if upload was successful
            session['uploaded_file'] = file.filename

    return redirect(url_for('upload_result'))

@app.route('/upload/result')
@login_required
def upload_result():
    # Get the filename from the session
    uploaded_file = session.get('uploaded_file', None)
    if uploaded_file is None:
        return render_template('upload_result.html',
                                file=uploaded_file, status="File upload wasn't successful")
    return render_template('upload_result.html',
                            file=uploaded_file, status="File upload was successful")

@app.route('/upload/approve')
@login_required
def approve_upload():
    file_name = sanitize_string(request.args.get('file_name'))
    file_password = request.args.get('file_password')
    if not file_name: return redirect(url_for('index'))

    if file_password is not None:
        file_password = sanitize_string(file_password)
        if approve_file(file_name, app.config['UPLOAD_FOLDER'], file_password):
            return "File approved"
        return "File not approved"
    elif check_access(session['user_name'], 9) and file_password is None:
        if approve_file(file_name, app.config['UPLOAD_FOLDER'], file_password, admin=True):
            return "File approved"
        return "File not approved"
    else: return "You are not allowed to approve files"

@app.route('/delete_image', methods=['POST'])
@login_required
def delete_image():
    if request.method != 'POST':
        return redirect(url_for('index'))

    if not check_access(session['user_name'], 1):
        return render_template('error/blocked.html', support_url=os.environ.get('SUPPORT_URL'))

    if not request.form['filename']:
        return redirect(url_for('index'))

    file_name = sanitize_string(request.form['filename'])

    user = get_user_from_users(session['user_name'])
    if not user: return redirect(url_for('login'))

    if not check_access(session['user_name'], 9):
        queue_files = user.get_user_files_queue()
        if not file_name in queue_files:
            uploads_files = user.get_user_files_uploads()
            if not file_name in uploads_files:
                return "User who sent the request to delete {file_name} isn't its owner"

    if not delete_file(file_name):
        return "Error while deleting image"
    return redirect(url_for('dashboard'))

@app.route('/management/users')
@login_required
def management_users():
    if not check_access(session['user_name'], 9):
        return redirect(url_for('index'))

    users_data = get_users_data_for_dashboard()
    return render_template('management/users.html', users_data=users_data)

@app.route('/management/approve')
@login_required
def management_approve():
    if not check_access(session['user_name'], 6):
        return redirect(url_for('index'))

    user = get_user_from_users(session['user_name'])
    if not user: return redirect(url_for('login'))

    queued_images = user.get_user_files_queue()
    return render_template('management/approve.html', queued_images=queued_images)

@app.route('/management/delete')
@login_required
def management_delete():
    if not check_access(session['user_name'], 6):
        return redirect(url_for('index'))

    user = get_user_from_users(session['user_name'])
    if not user: return redirect(url_for('login'))

    all_images = get_all_images_for_all_users()
    return render_template('management/delete.html', all_images=all_images)

@app.route('/management/set_role', methods=['POST'])
@login_required
def management_set_role():
    if request.method != 'POST':
        return render_template('errors/error.html', error_message=f"Wrong HTTP Method")

    if not check_access(session['user_name'], 9):
        return render_template('errors/error.html', error_message=f"You aren't allowed to access this page")

    try:
        role_name = sanitize_string(request.form['role_name'])
        target_user_name = sanitize_string(request.form['target_user_name'])
    except KeyError as e:
        logging(f"KeyError for url parameters: {e}")
        return render_template('index.html')

    user = get_user_from_users(session['user_name'])
    if not user: return redirect(url_for('login'))

    if not user.set_user_role(role_name):
        return render_template('errors/error.html', error_message=f"Role wasn't changed")

    return redirect(url_for('management_users'))

@app.route('/management/update_upload_limit', methods=['POST'])
@login_required
def management_update_upload_limit():
    if request.method != 'POST':
        return render_template('errors/error.html', error_message=f"Wrong HTTP Method")

    if not check_access(session['user_name'], 9):
        return render_template('errors/error.html', error_message=f"You aren't allowed to access this page")
    
    upload_limit = sanitize_string(request.form['upload_limit'])
    target_user_name = sanitize_string(request.form['target_user_name'])    
    try:
        upload_limit = sanitize_string(request.form['upload_limit'])
        target_user_name = sanitize_string(request.form['target_user_name'])
    except KeyError:
        return render_template('errors/error.html', error_message=f"Specified parameters aren't valid")
    
    if len(upload_limit) > 31 or len(target_user_name) > 100:
        return render_template('errors/error.html', error_message=f"Specified parameters are too large")

    try:
        upload_limit = int(upload_limit)
    except ValueError:
        return render_template('errors/error.html', error_message=f"Specified parameters aren't valid")

    user = get_user_from_users(target_user_name)
    if not user:
        return render_template('errors/error.html', error_message=f"Your user couldn't be found in the database")

    if not user.set_user_upload_limit(upload_limit):
        return render_template('errors/error.html', error_message=f"Upload limit {upload_limit} isn't valid")

    return redirect(url_for('management_users'))

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def page_not_found():
    return render_template('errors/404.html'), 404

@app.errorhandler(405)
def page_not_found():
    return render_template('errors/405.html'), 405

if __name__ == '__main__':
    app.run(debug=True)
