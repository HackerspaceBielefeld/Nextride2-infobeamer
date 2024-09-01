
import os
import json
import secrets

from flask import Blueprint, session, render_template, request, redirect, url_for

from helper import sanitize_string
from role_based_access import check_access
from filehandler import sanitize_filename


blueprint = Blueprint('pibooth', __name__, template_folder='extensions/pibooth/templates')

def load_config():
    # In case the config file do not exist, create it
    if not os.path.exists("extensions/pibooth/config.json"):
        with open("extensions/pibooth/config.json", "+w") as f:
            f.write('{"token": "' + secrets.token_urlsafe(64) + '"}')

    with open('extensions/pibooth/config.json', 'r') as config_file:
        return json.load(config_file)

def save_config(config:json):
    with open('extensions/pibooth/config.json', 'w') as config_file:
        json.dump(config, config_file)

def get_token():
    config = load_config()
    return config.get("token")

def renew_token():
    config = load_config()
    config['token'] = secrets.token_urlsafe(64)
    save_config(config)

@blueprint.route('/',  methods=['GET','POST'])
#@login_required
def index():
    user_name = session.get("user_name")
    if not check_access(user_name, 9):
        return error_page("You are not allowed to access this page")
    
    if request.method == "POST":
        renew_token()
        return redirect(url_for("pibooth.index"))
    else:
        token = get_token()
        url = request.host_url + url_for("pibooth.upload_extension_pibooth")[1:]
    return render_template('pibooth.html', url=url, token=token)


@blueprint.route('/upload', methods=['POST'])
#@login_required
def upload_extension_pibooth():
    req_pibooth_token = request.headers.get('token')
    req_pibooth_file = request.files.get('file')
    if not req_pibooth_token == get_token():
        return "Token not valid"
    elif not req_pibooth_file:
        return "No file received"

    file_name = sanitize_filename(req_pibooth_file.filename)
    file_path = os.path.join("static/uploads/", file_name)
    req_pibooth_file.save(file_path)
    return "success"

def error_page(error_message: str):
    error_message = sanitize_string(error_message, extend_allowed_chars=True)
    return render_template('errors/error.html', error_message=error_message)
