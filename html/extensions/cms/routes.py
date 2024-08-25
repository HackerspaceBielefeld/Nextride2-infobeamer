from flask import Blueprint, session, render_template, request, redirect, url_for

from helper import sanitize_string
from role_based_access import check_access

from extensions.cms.CMSConfig import get_cms_config, get_conn

blueprint = Blueprint('cms', __name__, template_folder='extensions/cms/templates')

@blueprint.route('/')
#@login_required
def index():
    user_name = session.get("user_name")
    if not check_access(user_name, 9):
        return error_page("You are not allowed to access this page")
    
    config = get_cms_config()

    return render_template('cms.html', config=config)

@blueprint.route('/update', methods=['POST'])
#@login_required
def update_extension_cms():
    user_name = session.get("user_name")
    if not check_access(user_name, 9):
        return error_page("You are not allowed to access this page")

    req_cms_config = request.form.getlist('selected_setting')
    if not req_cms_config: return error_page("No cms settings found")

    for setting in get_cms_config():
        if setting.name in req_cms_config:
            setting.activate()
        else:
            setting.deactivate()

    return redirect(url_for('cms.index'))

def error_page(error_message: str):
    error_message = sanitize_string(error_message, extend_allowed_chars=True)
    return render_template('errors/error.html', error_message=error_message)
