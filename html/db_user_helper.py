# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught
# pylint: disable=W0102

import os

from db_models import Users, db

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from helper import logging

# Load environment variables from .env file
load_dotenv()

def get_user_from_users(user_name: str):
    try:
        user = db.session.query(Users).filter(Users.name == user_name).first()
        if user: return user
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving an user from the users table: {e}")
    return False

def get_users_data_for_dashboard():
    users = db.session.query(Users).all()
    users_data = [{'id': user.id, 'user_name': user.name, 'user_role': user.role.name,
        'user_upload_limit': user.upload_limit, 'user_upload_amount': user.upload_amount}
        for user in users]
    return users_data


def add_user_to_users(user_name: str, user_upload_amount=0,
    user_upload_limit=os.environ.get('DEFAULT_USER_UPLOAD_LIMIT'), user_files=[]):

    if get_user_from_users(user_name):
        logging(f"User with the same username: {user_name} already exist in the users table")
        return False

    try:
        user = Users(user_name=user_name, user_upload_amount=user_upload_amount,
            user_upload_limit=int(user_upload_limit), user_files=user_files)
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as e:
        logging(f"An error occurred while adding an user to the users table: {e}")
        return False

    admin_users = os.environ.get('ADMIN_USERS').split(',')
    if user.name in admin_users:
        if not user.set_user_role("admin"):
            logging("User role couldn't be set as admin")
            return False
    return True

def remove_user_from_users(user_name: str):
    try:
        user = get_user_from_users(user_name)
        if user:
            db.session.delete(user)
            db.session.commit()
            return user
        logging("User to delete wasn't found in the users table")
        return False
    except SQLAlchemyError as e:
        logging(f"An error occurred while removing an user from the users table: {e}")
        return False
