# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught
# pylint: disable=W0102

"""
Database User Helper Module

This module provides functions to interact with the users table in the database, including retrieving user data,
adding new users, and removing users.

Functions:
    - get_user_from_users(user_name): Retrieve a user from the users table based on the username.
    - get_users_data_for_dashboard(): Retrieve user data for the dashboard.
    - add_user_to_users(user_name, user_upload_amount=0, user_upload_limit=None,
        user_role="default", user_files=[]): Add a new user to the users table.
    - remove_user_from_users(user_name): Remove a user from the users table.

Dependencies:
    - os: Provides functions for interacting with the operating system.
    - db_models.Users: Model class representing the users table in the database.
    - db_models.db: Database session object.
    - dotenv.load_dotenv: Loads environment variables from a .env file.
    - flask_sqlalchemy.SQLAlchemy: SQLAlchemy integration with Flask.
    - helper.logging: Custom logging function for error handling.

Exceptions:
    - SQLAlchemyError: Raised if an error occurs while interacting with the database.
"""

import os

from db_models import Users, db

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from helper import logging

# Load environment variables from .env file
load_dotenv()

def get_user_from_users(user_name: str):
    """
    Retrieve a user from the users table based on the username.

    Args:
        user_name (str): The username of the user.

    Returns:
        Users: The user object if found, False otherwise.
    """

    try:
        return db.session.query(Users).filter(Users.user_name == user_name).first()
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving an user from the users table: {e}")
    return False

def get_users_data_for_dashboard():
    """
    Retrieve user data for the dashboard.

    Returns:
        list: A list of dictionaries containing user data.
    """

    users = db.session.query(Users).all()
    users_data = [{'id': user.id, 'user_name': user.user_name, 'user_role': user.user_role} for user in users]
    return users_data


def add_user_to_users(user_name: str, user_upload_amount=0,
    user_upload_limit=os.environ.get('DEFAULT_USER_UPLOAD_LIMIT'), user_role="default", user_files=[]):
    """
    Add a new user to the users table.

    Args:
        user_name (str): The username of the new user.
        user_upload_amount (int, optional): The upload amount of the new user (default is 0).
        user_upload_limit (int, optional): The upload limit of the new user (default is None).
        user_role (str, optional): The role of the new user (default is "default").
        user_files (list, optional): The files associated with the new user (default is None).

    Returns:
        bool: True if the user was added successfully, False otherwise.

    Raises:
        Exception: If an error occurs while adding the user to the database.
    """

    try:
        user = Users(user_name=user_name, user_upload_amount=user_upload_amount,
            user_upload_limit=int(user_upload_limit), user_role=user_role, user_files=user_files)
        if get_user_from_users(user_name) is not None:
            logging(f"User with the same username: {user_name} already exist in the users table")
            return False
        db.session.add(user)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        logging(f"An error occurred while adding an user to the users table: {e}")
        return False

def remove_user_from_users(user_name: str):
    """
    Remove a user from the users table.

    Args:
        user_name (str): The username of the user to be removed.

    Returns:
        Users: The user object if removed successfully, False otherwise.
    
    Raises:
        Exception: If an error occurs while removing the user to the database.
    """

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
