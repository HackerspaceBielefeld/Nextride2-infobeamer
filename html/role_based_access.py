"""
@file user_role_access.py
@brief This module provides functions for managing user roles and access control.

@details The module includes functions to check if a user has the necessary 
            permissions based on their role, including admin and moderator checks.
            It also verifies if the content management system (CMS) is active to 
            enforce access controls accordingly.

@dependencies
- `db_user_helper` for user role retrieval.
- `db_extension_helper` for checking CMS status.
- Custom logging function from the `helper` module.

@author Inflac
@date 2024-10-04
"""

import os
from db_user_helper import get_user_from_users
from db_extension_helper import get_extension_from_config
from helper import logging



def check_admin(user_name: str) -> bool:
    """
    Check if the user has admin privileges.

    @param user_name The username to check.
    @return True if the user is an admin, False otherwise.
    """

    admin_users = os.environ.get('ADMIN_USERS', '').split(',')
    if user_name in admin_users:
        logging(f"User '{user_name}' is an admin.")
        return True
    logging(f"User '{user_name}' is not an admin.")
    return False

def check_moderator(user_name: str) -> bool:
    """
    Check if the user has moderator privileges.

    @param user_name The username to check.
    @return True if the user is a moderator, False otherwise.
    """

    user = get_user_from_users(user_name)
    if not user:
        logging(f"User '{user_name}' couldn't be found.")
        return False

    if user.role.name != 'moderator':
        logging(f"User '{user_name}' isn't a moderator.")
        return False
    
    logging(f"User '{user_name}' is a moderator.")
    return True


def cms_active() -> bool:
    """
    Check if the content management system (CMS) is active.

    @return True if the CMS is active, False otherwise.
    """

    cms = get_extension_from_config("cms")
    if cms:
        logging("CMS is active.")
        return cms.active
    logging("CMS is not active.")
    return False


def check_access(user_name: str, min_req_role_id: int) -> bool:
    """
    Check if the user has the required access based on their role.

    @param user_name The username to check.
    @param min_req_role_id The minimum required role ID for access.
    @return True if the user has the required access, False otherwise.
    """
    user = get_user_from_users(user_name)
    if not user:
        logging(f"User '{user_name}' couldn't be found.")
        return False

    if not cms_active():
        if user.role.id >= 9:
            logging(f"User '{user_name}' has sufficient access (role ID: {user.role.id}).")
            return True
        logging(f"User '{user_name}' does not have sufficient access (role ID: {user.role.id}).")
        return False

    if user.role.id >= min_req_role_id:
        logging(f"User '{user_name}' has sufficient access (role ID: {user.role.id}).")
        return True
    
    logging(f"User '{user_name}' does not have sufficient access (role ID: {user.role.id}).")
    return False
