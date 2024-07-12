from flask import Blueprint, session, render_template, request, redirect, url_for
from helper import sanitize_string
from role_based_access import check_access

blueprint = Blueprint('cms', __name__, template_folder='extensions/cms/templates')


@blueprint.route('/')
#@login_required
def index():
    try:
        user_name = session['user_name']
    except KeyError:
        return error_page("You are not allowed to access this page")
    
    if not check_access(session['user_name'], 9):
        return error_page("You are not allowed to access this page")
    
    return render_template('cms.html')

def error_page(error_message: str):
    error_message = sanitize_string(error_message, extend_allowed_chars=True)
    return render_template('errors/error.html', error_message=error_message)
