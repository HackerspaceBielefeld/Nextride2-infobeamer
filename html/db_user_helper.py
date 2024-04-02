import os

from flask_sqlalchemy import SQLAlchemy
from db_models import Users, db

from dotenv import load_dotenv

from helper import logging

# Load environment variables from .env file
load_dotenv()

def get_user_from_users(user_name: str):
    try:
        return db.session.query(Users).filter(Users.user_name == user_name).first()
    except Exception as e:
        logging(f"An error occurred while retrieving an user from the users table: {e}")
    return False

def add_user_to_users(user_name: str, user_upload_amount=0, user_upload_limit=os.environ.get('DEFAULT_USER_UPLOAD_LIMIT'), user_role="default", user_files=[]):
    try:
        user = Users(user_name=user_name, user_upload_amount=user_upload_amount, user_upload_limit=user_upload_limit, user_role=user_role, user_files=user_files)
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as e:
        logging(f"An error occurred while adding an user to the users table: {e}")
        return False

def remove_user_from_users(user_name: str):
    try:
        user = get_user_from_users(user_name)
        if user:
            db.session.delete(user)
            db.session.commit()
            return user
        logging("User to delete wasn't found in the users table")
        return False
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"An error occurred while removing an user from the users table: {e}")
        return False
