from flask import Blueprint, session, render_template, request, redirect, url_for
from extensions.mastodon.db_extension_mastodon_helper import add_mastodon_tag, get_all_mastodon_tags, get_mastodon_tag_by_name, update_mastodon_tag
from helper import sanitize_string
from role_based_access import check_access

# Define Blueprint
blueprint = Blueprint('mastodon', __name__, template_folder='extensions/mastodon/templates')

@blueprint.route('/')
#@login_required
def management_extension_mastodon():
    try:
        user_name = session['user_name']
    except KeyError:
        return error_page("You are not allowed to access this page")
    
    if not check_access(session['user_name'], 9):
        return error_page("You are not allowed to access this page")
    
    tags = get_all_mastodon_tags()

    return render_template('mastodon.html', tags=tags)


@blueprint.route('/update', methods=['POST'])
#@login_required
def update_extension_mastodon():
    try:
        user_name = session['user_name']
    except KeyError:
        return error_page("You are not allowed to access this page")

    if not check_access(session['user_name'], 9):
        return error_page("You are not allowed to access this page")

    req_tags = request.form.get('tags')
    req_limit = request.form.get('limit')

    if not req_tags or not req_limit:
        return error_page("Specified parameters aren't valid")

    try:
        limit = int(req_limit)
    except ValueError:
        return error_page("Specified parameters aren't valid")

    if len(req_tags) > 500 or limit < 0 or limit > 20:
        return error_page("Specified parameters are too large or limit is less than zero")

    unsanitized_tags = req_tags.split("\n")
    for tag in unsanitized_tags:
        tag = sanitize_string(tag)

        if len(tag) == 0: continue

        tag_elem = get_mastodon_tag_by_name(tag)
        if tag_elem:
            update_mastodon_tag(tag_elem.name, limit)
        elif not add_mastodon_tag(tag, limit):
            return error_page("An error occured while adding a new Tag")

    return redirect(url_for('mastodon.management_extension_mastodon'))

def error_page(error_message: str):
    error_message = sanitize_string(error_message, extend_allowed_chars=True)
    return render_template('errors/error.html', error_message=error_message)