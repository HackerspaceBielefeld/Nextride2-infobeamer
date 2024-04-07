from helper import logging

from db_user_helper import get_user_from_users

def check_admin(user_name:str):
    user = get_user_from_users(user_name)
    if not user.user_role == 'default':
        logging(f"User {user_name} isn't an admin")
        return False
    return True