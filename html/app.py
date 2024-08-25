# pylint: skip-file
import os
import sys

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from authlib.integrations.flask_client import OAuth

from dotenv import load_dotenv
from functools import wraps

from filehandler import sanitize_file, safe_file, delete_file, get_all_images_for_all_users, get_uploads
from queuehandler import approve_file
from db_models import db, create_roles, create_extensions
from db_user_helper import add_user_to_users, get_user_from_users, get_users_data_for_dashboard
from db_extension_helper import get_extensions_from_extensions
from helper import sanitize_string

from role_based_access import check_access, cms_active, check_admin

import importlib.util

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
    create_extensions()

# Configure flask app with parameters from .env file
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
app.config['QUEUE_FOLDER'] = os.environ.get('QUEUE_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

# Cookie flags
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'lax'

# Ensure the extensions folder is in the PYTHONPATH
extensions_folder = os.path.join(os.path.dirname(__file__), 'extensions')
sys.path.insert(0, extensions_folder)

# Load extensions
for extension_name in os.listdir(extensions_folder):
    extension_path = os.path.join(extensions_folder, extension_name)
    if os.path.isdir(extension_path):
        spec = importlib.util.spec_from_file_location(extension_name, os.path.join(extension_path, 'routes.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        app.register_blueprint(module.blueprint, url_prefix=f'/management/extensions/{extension_name}')

# create_folder
os.makedirs("static/uploads/system", exist_ok=True)
os.makedirs("static/queue", exist_ok=True)

oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.environ.get('GITHUB_CLIENT_ID'),
    client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'user:name'},
)

def login_required(access_level_required=1):
    """
    Decorator function to protect routes that require authentication.
    Redirects unauthenticated users to the login page.
    """
    def decorator(view):
        @wraps(view)
        def decorated_view(*args, **kwargs):
            # Redirect to the login route if the user do not have a session
            if not session.get('token'):
                return redirect(url_for('login', next=request.url))

            # If username from session don't dissolve to a user obj, return index page
            user = get_user_from_users(session['user_name'])
            if not user:
                return redirect(url_for('logout')) # User has a session token but no user exists in db => log him out

            session['user_role'] = user.role.id

            # Check access level
            if not check_access(user.name, access_level_required):
                return render_template('errors/blocked.html', support_url=os.environ.get('SUPPORT_URL'))

            return view(*args, **kwargs)
        return decorated_view
    return decorator

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return github.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = github.authorize_access_token()
    if not token: 
        return error_page("Login failed")

    user = github.get('https://api.github.com/user', token=token)
    if not user.ok:
        return error_page("Failed to fetch user data from GitHub")

    user_data = user.json()
    session['user_data'] = user_data
    session['user_name'] = user_data['login']
    
    user = get_user_from_users(user_data['login'])

    if cms_active():
        if user:                                            # Authenticate existing user
            session['token'] = token
            session['user_role'] = user.role.id
            return redirect(url_for('dashboard'))
        else:                                               # Add a new user
            if add_user_to_users(user_data['login']):
                return redirect(url_for('dashboard'))
            return error_page("User couldn't be added to the database")
    else:
        if user:
            if user.role.id < 9:                            # CMS deactivated => redirect existing non admin users to index
                return redirect(url_for('index'))
            else:                                           # Allow existing admin users to login even CMS is deactivated
                session['token'] = token
                session['user_role'] = user.role.id
                return redirect(url_for('dashboard'))
        else:                                               # CMS deactivated and user do not exist
            if check_admin(user_data['login']):             # CMS deactivated but user is admin => create a user
                if add_user_to_users(user_data['login']):
                    return redirect(url_for('dashboard'))
                return error_page("User couldn't be added to the database")
            else:
                return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    if session.get('token'):
        session.clear()
        return render_template('logout.html')
    else:
        return error_page("You are already logged out")

@app.route('/', methods=['GET'])
def index():
    uploaded_images, extension_images = get_uploads(app.config['UPLOAD_FOLDER'], extensions_folder)
    return render_template('index.html', uploaded_images=uploaded_images, extension_images=extension_images)

@app.route('/system', methods=['GET'])
def system():
    system_images = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], "system"))
    return render_template('system.html', uploaded_images=system_images)


@app.route('/dashboard', methods=['GET'])
@login_required(access_level_required=1)
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
@login_required(access_level_required=1)
def upload_file():
    if not request.files.get('file'):
        return error_page("No file selected")
    file = sanitize_file(request.files.get('file'), app.config['MAX_CONTENT_LENGTH'])

    # If the file isn't valid the upload_result page will not find a file in the session
    # and so return an error message indicating the upload wasn't successful.
    if file != False:        
        if safe_file(file, app.config['QUEUE_FOLDER'], session['user_name']):
            session['uploaded_file'] = file.filename
    return redirect(url_for('upload_result'))

@app.route('/upload/result', methods=['GET'])
@login_required(access_level_required=1)
def upload_result():
    uploaded_file = session.get('uploaded_file', None)
    return render_template('upload_result.html', file=uploaded_file)

@app.route('/upload/approve')
@login_required() #TODO Special case because of email approves
def approve_upload():
    if not request.args.get('file_name'):
        return error_page("Specified parameters aren't valid")
    file_name = sanitize_string(request.args.get('file_name'))
    if len(file_name) > 100:
        return error_page("Specified parameters are too large")
    file_password = None
    if request.args.get('file_password'):
        file_password = sanitize_string(request.args.get('file_password'))
        if len(file_password) > 64:
            return error_page("Specified parameters are too large")

    if file_password is not None:
        if approve_file(file_name, app.config['UPLOAD_FOLDER'], file_password):
            return "File approved"
        return error_page("File not approved")
    elif check_access(session['user_name'], 6) and file_password is None:
        if approve_file(file_name, app.config['UPLOAD_FOLDER'], file_password, admin=True):
            return redirect(url_for('management_approve'))
        return error_page("File not approved")

    return error_page("You are not allowed to approve files")

@app.route('/delete_image', methods=['POST'])
@login_required(access_level_required=1)
def delete_image():
    if not request.form.get('file_name'):
        return error_page("No file selected")
    file_name = sanitize_string(request.form.get('file_name'))
    if len(file_name) > 100:
        return error_page("file name too long")

    user = get_user_from_users(session['user_name'])
    if not user: return redirect(url_for('login'))

    if not check_access(session['user_name'], 6):
        queue_files = user.get_user_files_queue()
        if not file_name in queue_files:
            uploads_files = user.get_user_files_uploads()
            if not file_name in uploads_files:
                return error_page("You can not delete the requested image because you are not its owner")

    if not delete_file(file_name):
        return error_page("Error while deleting the file")
    return redirect(url_for('dashboard'))

@app.route('/management/users', methods=['GET'])
@login_required(access_level_required=9)
def management_users():
    users_data = get_users_data_for_dashboard()
    return render_template('management/users.html', users_data=users_data)

@app.route('/management/approve', methods=['GET'])
@login_required(access_level_required=6)
def management_approve():
    all_images = get_all_images_for_all_users(queue_only=True)
    return render_template('management/approve.html', all_images=all_images)

@app.route('/management/delete', methods=['GET'])
@login_required(access_level_required=6)
def management_delete():
    all_images = get_all_images_for_all_users()
    return render_template('management/delete.html', all_images=all_images)

@app.route('/management/set_role', methods=['POST'])
@login_required(access_level_required=9)
def management_set_role():
    if not request.form.get('role_name') or not request.form.get('target_user_name'):
        return error_page("Specified parameters aren't valid")
    role_name = sanitize_string(request.form.get('role_name'))
    target_user_name = sanitize_string(request.form.get('target_user_name'))    

    if len(role_name) > 10 or len(target_user_name) > 100:
        return error_page("Specified parameters are too large")

    user = get_user_from_users(target_user_name)
    if not user: return error_page("The user whichs role you're trying to modify do not exist")

    if not user.set_user_role(role_name):
        return error_page("An error occured - The role was not changed")

    return redirect(url_for('management_users'))

@app.route('/management/update_upload_limit', methods=['POST'])
@login_required(access_level_required=9)
def management_update_upload_limit():
    if not request.form.get('upload_limit') or not request.form.get('target_user_name'):
        return error_page("Specified parameters aren't valid")
    upload_limit = sanitize_string(request.form.get('upload_limit'))
    target_user_name = sanitize_string(request.form.get('target_user_name'))

    if len(upload_limit) > 12 or len(target_user_name) > 100:
        return error_page("Specified parameters are too large")

    try:
        upload_limit = int(upload_limit)
    except ValueError:
        return error_page("Specified parameters aren't valid")

    user = get_user_from_users(target_user_name)
    if not user: return error_page("The user whichs upload limit you're trying to modify do not exist")

    if not user.set_user_upload_limit(upload_limit):
        return error_page("An error occured - The upload limit was not updated")

    return redirect(url_for('management_users'))


@app.route('/management/extensions', methods=['GET'])
@login_required(access_level_required=9)
def management_extensions():
    extensions = get_extensions_from_extensions()
    return render_template('management/extension.html', extensions=extensions)

@app.route('/management/update_extensions', methods=['POST'])
@login_required(access_level_required=9)
def management_update_extensions():
    req_extensions = request.form.getlist('selected_extensions')
    if not req_extensions: req_extensions = []

    for extension in get_extensions_from_extensions():
        if extension.name in req_extensions: 
            extension.activate()
        else:
            extension.deactivate()

    return redirect(url_for('management_extensions'))


@app.route('/faq', methods=['POST'])
def faq():
    return render_template('faq.html')

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def error_page(error_message: str):
    error_message = sanitize_string(error_message, extend_allowed_chars=True)
    return render_template('errors/error.html', error_message=error_message)

@app.errorhandler(404)
def page_not_found(e):
    return error_page("404 - Page not found"), 404

@app.errorhandler(405)
def page_wrong_method(e):
    return error_page("405 - Method Not Allowed"), 405

@app.errorhandler(413)
def req_entity_to_large(e):
    return error_page(f"413 - File is larger than '{app.config['MAX_CONTENT_LENGTH']}'"), 413

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
