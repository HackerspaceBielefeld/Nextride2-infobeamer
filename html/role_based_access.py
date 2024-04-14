"""
Module for user role management.
"""
from db_user_helper import get_user_from_users

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
    if not user.role.name == 'admin':
        logging(f"User {user_name} isn't an admin")
        return False
    return True
