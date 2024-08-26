"""
Module for user role management.
"""
import os

from db_user_helper import get_user_from_users
from db_extension_helper import get_extension_from_config

from helper import logging


def check_admin(user_name: str):
    admin_users = os.environ.get('ADMIN_USERS').split(',')
    if user_name in admin_users:
        return True
    return False

def check_moderator(user_name: str):
    user = get_user_from_users(user_name)
    if not user:
        logging("User couldn't be found")
        return False

    if not user.role.name == 'moderator':
        logging(f"User {user_name} isn't a moderator")
        return False
    return True


def cms_active():
    cms = get_extension_from_config("cms")
    if cms:
        return cms.active
    return False

def check_access(user_name: str, min_req_role_id: int):
    user = get_user_from_users(user_name)
    if not user:
        logging("User couldn't be found")
        return False

    if not cms_active():
        if user.role.id >= 9: return True
        return False

    if user.role.id >= min_req_role_id:
        return True
    return False
