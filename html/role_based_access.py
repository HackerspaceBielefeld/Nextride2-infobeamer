"""
Module for user role management.
"""
from db_user_helper import get_user_from_users
from db_extension_helper import get_extension_from_config

from helper import logging

def check_admin(user_name: str):
    """
    Check if a user is an admin.

    Args:
        user_name (str): The username to check.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    user = get_user_from_users(user_name)
    if not user:
        logging("User couldn't be found")
        return False

    if not user.role.name == 'admin':
        logging(f"User {user_name} isn't an admin")
        return False
    return True

def check_moderator(user_name: str):
    """
    Check if a user is a moderator.

    Args:
        user_name (str): The username to check.

    Returns:
        bool: True if the user is a moderator, False otherwise.
    """

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
    return cms.active

def check_access(user_name: str, min_req_role_id: int):
    """
    Check if a user has a role thats allowed for access based on the
    users role id.

    Args:
        user_name (str): The username to check.

    Returns:
        bool: True if the user is allowed, False otherwise.
    """
    user = get_user_from_users(user_name)
    if not user:
        logging("User couldn't be found")
        return False

    if not cms_active():
        if user.role.id >= 10: return True
        return False

    if user.role.id >= min_req_role_id:
        return True
    return False