"""
@file db_user_helper.py
@brief This module provides helper functions to interact with the 'Users' table in the database.

@details This module includes functions to retrieve user information, add new users,
            and remove users from the database. SQLAlchemy is used for database interaction,
            and exceptions are handled with proper logging.

@dependencies
- SQLAlchemy for database ORM
- Environment variables for configuration
- Users model from db_models

@author Inflac
@date 2024
"""

import os
import logging

from typing import List, Dict, Union

from db_models import Users, db
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger()


def get_user_from_users(user_name: str) -> Union[Users, bool]:
    """
    Retrieve a user from the users table by username.

    This function queries the database for a user with the specified username.
    If the user exists, it returns the Users object; otherwise, it returns False.

    @param user_name The username to look for.
    @return The Users object if found, False otherwise.

    @exception SQLAlchemyError If there is an error while querying the database.
    """
    try:
        user = db.session.query(Users).filter(Users.name == user_name).first()
        if user:
            logger.debug(f"User '{user_name}' found in the users table.")
            return user
        else:
            logger.debug(f"User '{user_name}' not found in the users table.")
            return False
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while retrieving a user from the users table: {e}")
        return False

def get_users_data_for_dashboard() -> List[Dict[str, Union[int, str]]]:
    """
    Retrieve all users' data for the dashboard.

    This function retrieves all users from the database and formats their data
    into a list of dictionaries, which can be easily displayed on a dashboard.

    @return A list of dictionaries containing user data, including ID, username,
            role, upload limit, and upload amount.
    """
    try:
        users = db.session.query(Users).all()
        users_data = [{
            'id': user.id,
            'user_name': user.name,
            'user_role': user.role.name,
            'user_upload_limit': user.upload_limit,
            'user_upload_amount': user.upload_amount
        } for user in users]
        logger.debug("Successfully retrieved users data for dashboard.")
        return users_data
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while retrieving users data: {e}")
        return []


def add_user_to_users(
    user_name: str,
    user_upload_amount: int = 0,
    user_upload_limit: int = int(os.environ.get('DEFAULT_USER_UPLOAD_LIMIT', 10)),  # Default to 10 if not set
    user_files: List[str] = None
    ) -> bool:
    """
    Add a new user to the users table.

    This function adds a user with specified attributes to the users table. 
    If a user with the same username already exists, it will not add a duplicate.

    @param user_name The username to add.
    @param user_upload_amount The initial upload amount for the user.
    @param user_upload_limit The maximum upload limit for the user.
    @param user_files A list of files associated with the user (default is an empty list).

    @return True if the user is added successfully, False otherwise.

    @exception SQLAlchemyError If there is an error while adding the user to the database.
    """
    user_files = user_files or []  # Default to an empty list if None

    if get_user_from_users(user_name):
        logger.warning(f"User '{user_name}' already exists in the users table.")
        return False

    try:
        user = Users(user_name=user_name, user_upload_amount=user_upload_amount,
                        user_upload_limit=user_upload_limit, user_files=user_files)
        db.session.add(user)
        db.session.commit()
        logger.info(f"User '{user_name}' added to the users table successfully.")
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while adding a user to the users table: {e}")
        return False

    admin_users = os.environ.get('ADMIN_USERS', '').split(',')
    if user.name in admin_users and not user.set_user_role("admin"):
        logger.warning("Failed to set user role as admin.")
        return False

    return True

def remove_user_from_users(user_name: str) -> Union[Users, bool]:
    """
    Remove a user from the users table by username.

    This function removes a user with the specified username from the database. 
    If the user is not found, it logs an appropriate message and returns False.

    @param user_name The username of the user to remove.
    
    @return The removed Users object if successful, False otherwise.

    @exception SQLAlchemyError If there is an error while removing the user from the database.
    """
    try:
        user = get_user_from_users(user_name)
        if user:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"User '{user_name}' removed from the users table successfully.")
            return user

        logger.warning(f"User '{user_name}' not found in the users table.")
        return False
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while removing a user from the users table: {e}")
        return False
