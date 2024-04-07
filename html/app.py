import os

from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
#from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
from functools import wraps

from filehandler import sanitize_file, safe_file, delete_file
from queuehandler import approve_file
from db_models import db
from db_user_helper import add_user_to_users, get_user_from_users

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
        return view(*args, **kwargs)
    return decorated_view

def admin_required(view):
    # TODO check if user is admin
    return

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = github.authorize_access_token()
    if token:
        session['token'] = token
        user = github.get('https://api.github.com/user', token=token)
        if user.ok:
            user_data = user.json()
            session['user_data'] = user_data
            session['user_name'] = user_data['login']
            add_user_to_users(user_data['login'])
            return redirect(url_for('dashboard'))
        else:
            return "Failed to fetch user data from GitHub."
    else:
        return "Login failed."


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
    return render_template('dashboard.html', uploaded_images=uploaded_images, queued_images=queued_images)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']

        file = sanitize_file(file, app.config['MAX_CONTENT_LENGTH'])
        if file != False:        
            if safe_file(file,app.config['QUEUE_FOLDER'], session['user_name']):
                # Store the filename in the session if upload was successful
                session['uploaded_file'] = file.filename

        return redirect(url_for('upload_result'))
    else:
        return 

@app.route('/upload/result')
@login_required
def upload_result():
    # Get the filename from the session
    uploaded_file = session.get('uploaded_file', None)
    if uploaded_file is None:
        return render_template('upload_result.html', file=uploaded_file, status="File upload wasn't successful")
    return render_template('upload_result.html', file=uploaded_file, status="File upload was successful")

@app.route('/upload/approve')
@login_required
def approve_upload():
    file_name = request.args.get('file_name')
    file_password = request.args.get('file_password')
    if file_name and file_password:
        approve_file(file_name, app.config['UPLOAD_FOLDER'], file_password)
        return "File approved"
    else: return "You are not allowed to approve files"

@app.route('/delete_image', methods=['POST'])
@login_required
def delete_image():
    if request.method == 'POST':
        file_name = request.form['filename']
        user_name = session['user_name']
    
    user = get_user_from_users(user_name)
    if not user: return False

    queue_files = user.get_user_files_queue()
    if not file_name in queue_files:
        uploads_files = user.get_user_files_uploads()
        if not file_name in uploads_files:
            return "User who sent the request to delete {file_name} isn't its owner"

    if not delete_file(file_name):
        return "Error while deleting image"
    return redirect(url_for('dashboard'))

@app.route('admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(405)
def page_not_found(error):
    return render_template('errors/405.html'), 405

if __name__ == '__main__':
    app.run(debug=True)
