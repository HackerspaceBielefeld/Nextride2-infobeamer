import os

from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from functools import wraps

from filehandler import sanitize_file, safe_file

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
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
            # You can use the user data to create or authenticate users in your system
            session['user_data'] = user_data
            return render_template('dashboard.html')
        else:
            return "Failed to fetch user data from GitHub."
    else:
        return "Login failed."


@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Clear session data related to uploaded file
    session.pop('uploaded_file', None)

    # Get list of uploaded images
    uploaded_images = os.listdir(app.config['UPLOAD_FOLDER'])    
    return render_template('dashboard.html', uploaded_images=uploaded_images)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']

        file = sanitize_file(file, app.config['MAX_CONTENT_LENGTH'])
        if file == False:
            return upload_result(status="File upload wasn't successful")
        
        safe_file(file, app.config['QUEUE_FOLDER'])
        
        # Store the filename in the session
        session['uploaded_file'] = file.filename
        
        return redirect(url_for('upload_result'))

@app.route('/upload/result')
@login_required
def upload_result():
    # Get the filename from the session
    uploaded_file = session.get('uploaded_file', None)
    if uploaded_file is None:
        return render_template('upload_result.html', file=uploaded_file, status="File upload wasn't successful")
    return render_template('upload_result.html', file=uploaded_file, status="File upload was successful")

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
