"""
@file db_file_helper.py
@brief This module provides helper functions to interact with the 'Uploads' and 'Queue' tables in the database.

This module includes functions to check file upload limits and manage uploads and file processing in a queue.
SQLAlchemy is used for database interaction, and exceptions are handled with proper logging.

@dependencies
- SQLAlchemy for database ORM
- Environment variables for configuration
- Custom logging function from the helper module
- Uploads and Queue models from db_models

@author Inflac
@date 2024-10-04
"""

import os
from sqlalchemy.exc import SQLAlchemyError
from typing import Union
from db_models import Uploads, Queue, db
from db_user_helper import get_user_from_users
from helper import logging


def check_global_upload_limit() -> bool:
    """
    @brief Check if the global upload limit has been reached.
    
    This function retrieves the current number of uploaded files from the database
    and compares it against the global upload limit specified in the environment variables.
    
    @return True if the number of uploads is below the global limit, False otherwise.
    
    @exception SQLAlchemyError Logs an error message if an exception occurs while querying the database.
    """
    try:
        GLOBAL_UPLOAD_LIMIT = int(os.environ.get('GLOBAL_UPLOAD_LIMIT', '100'))  # Default to 100 if not set

        num_files = db.session.query(Uploads).count()

        if num_files >= GLOBAL_UPLOAD_LIMIT:
            logging(f"Global upload limit of {GLOBAL_UPLOAD_LIMIT} reached. Current count: {num_files}")
            return False

        logging(f"Current upload count: {num_files}. Limit not reached.")
        return True
    except SQLAlchemyError as e:
        logging(f"Error while retrieving number of uploaded files: {e}")
        return False


def get_file_from_queue(file_name: str) -> Union[Queue, None, bool]:
    """
    @brief Retrieve a file from the Queue table by the file name.
    
    This function searches the database's Queue table for an entry that matches the
    provided file name and returns the first matching record, if found.

    @param file_name The name of the file to retrieve from the queue.
    @return The first matching Queue object if found, None if no match is found, False if an error occurs.
    
    @exception SQLAlchemyError Logs an error message if an exception occurs while querying the database.
    """
    try:
        file_entry = db.session.query(Queue).filter(Queue.file_name == file_name).first()
        
        if file_entry:
            logging(f"File '{file_name}' successfully retrieved from the queue.")
            return file_entry
        else:
            logging(f"No file with the name '{file_name}' found in the queue.")
            return None
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving the file '{file_name}' from the queue: {e}")
        return False


def add_file_to_queue(file_name: str, file_path: str, file_password: str, file_owner: str) -> bool:
    """
    @brief Add a file to the queue for review.
    
    This function adds a file to the queue by creating a new entry in the Queue table. 
    It first validates that the file owner exists and can accept the file. 
    If the file is successfully added to the queue, the function returns True.
    
    @param file_name The name of the file to be added to the queue.
    @param file_path The path to the file on the server.
    @param file_password The password associated with the file.
    @param file_owner The username of the user who owns the file.
    
    @return True if the file is successfully added to the queue and committed to the database.
            False if the file owner is not found, an error occurs while updating the user's file table, 
            or if there is a database error during the commit process.
    """

    # Validate the file owner
    user = get_user_from_users(file_owner)
    if not user:
        logging(f"File owner '{file_owner}' could not be found.")
        return False
    
    # Try adding the file to the user's file list
    if not user.add_user_file(file_name, uploads=False):
        logging(f"Failed to add file '{file_name}' to user '{file_owner}' file table.")
        return False

    # Create a new Queue entry and add it to the session
    try:
        queue_entry = Queue(
            file_name=file_name,
            file_path=file_path,
            file_password=file_password,
            file_owner=file_owner
        )
        db.session.add(queue_entry)
        db.session.commit()

        logging(f"File '{file_name}' successfully added to the queue.")
        return True
    except SQLAlchemyError as e:
        logging(f"An error occurred while adding file '{file_name}' to the queue: {e}")
        db.session.rollback()  # Rollback to undo any partial changes in case of error
        return False


def remove_file_from_queue(file_name: str) -> Union[Queue, bool]:
    """
    @brief Remove a file from the queue table by file name.
    
    This function searches the queue for a file by its name and removes the corresponding
    entry from the database. It also ensures that the file is removed from the owner's record 
    in the users table. 

    @param file_name The name of the file to be removed from the queue.
    
    @return The removed Queue object if successful, False if an error occurs or if the file
            or owner is not found.
    
    @exception SQLAlchemyError Logs an error message if an exception occurs during the database operation.
    """

    # Retrieve the file entry from the queue
    upload = get_file_from_queue(file_name)
    if not upload:
        logging(f"File '{file_name}' to delete was not found in the queue table.")
        return False

    # Retrieve the owner of the file
    user = get_user_from_users(upload.file_owner)
    if not user:
        logging(f"File owner '{upload.file_owner}' could not be found.")
        return False

    # Remove the file from the user's record
    if not user.remove_user_file(file_name, uploads=False):
        logging(f"Failed to remove file '{file_name}' from the user's record in the database.")
        return False

    # Delete the file entry from the queue table
    try:
        db.session.delete(upload)
        db.session.commit()

        logging(f"File '{file_name}' successfully removed from the queue.")
        return upload
    except SQLAlchemyError as e:
        logging(f"An error occurred while removing file '{file_name}' from the queue: {e}")
        db.session.rollback()  # Rollback to undo any partial changes in case of error
        return False


def get_file_from_uploads(file_name: str) -> Union[Uploads, None, bool]:
    """
    @brief Retrieve a file from the uploads table by the file name.
    
    This function searches the database's uploads table for an entry that matches the
    provided file name and returns the first matching record, if found.
    
    @param file_name The name of the file to retrieve from the uploads table.
    
    @return The first matching Uploads object if found, None if no matching file is found, 
            and False if an error occurs during the database query.
    
    @exception SQLAlchemyError Logs an error message if an exception occurs during the database operation.
    """
    try:
        # Attempt to query the uploads table for the specified file name
        file_record = db.session.query(Uploads).filter(Uploads.file_name == file_name).first()

        if file_record:
            logging(f"File '{file_name}' retrieved from the uploads table.")
            return file_record
        else:
            logging(f"File '{file_name}' not found in the uploads table.")
            return None

    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving file '{file_name}' from the uploads table: {e}")
        return False


def add_file_to_uploads(file_name: str, file_path: str, file_owner: str) -> bool:
    """
    @brief Add a file to the uploads table for public access.

    This function creates a new entry in the Uploads table for a file to be accessible publicly.
    Before adding the file, it verifies the file owner exists and is eligible to upload files. 
    If successful, the file is added to the database and the function returns True. Otherwise, 
    it logs an appropriate error message and returns False.

    @param file_name The name of the file to be uploaded.
    @param file_path The server path where the file is stored.
    @param file_owner The username of the user who owns the file.

    @return True if the file is successfully added to the uploads table and committed to the database.
            False if the file owner cannot be found, the file could not be added to the user's record,
            or if a database error occurs during the commit.

    @exception SQLAlchemyError Logs an error message if an exception occurs during the database operation.
    """

    # Verify the file owner exists in the system
    user = get_user_from_users(file_owner)
    if not user:
        logging(f"File owner '{file_owner}' couldn't be found.")
        return False

    # Try to add the file to the user's upload record
    if not user.add_user_file(file_name, uploads=True):
        logging(f"Failed to add file '{file_name}' to user '{file_owner}' record.")
        return False

    # Attempt to add the file to the uploads table in the database
    try:
        new_upload = Uploads(file_name=file_name, file_path=file_path, file_owner=file_owner)
        db.session.add(new_upload)
        db.session.commit()
        logging(f"File '{file_name}' successfully added to uploads by user '{file_owner}'.")
        return True
    except SQLAlchemyError as e:
        logging(f"An error occurred while adding file '{file_name}' to the uploads table: {e}")
        db.session.rollback()  # Rollback to undo any partial changes in case of error
        return False


def remove_file_from_uploads(file_name: str) -> Union[Uploads, bool]:
    """
    @brief Remove a file from the uploads table by file name.

    This function searches for a file in the uploads table by its name, removes the corresponding
    entry from the database, and ensures the file is removed from the user's records. The function
    handles possible errors and logs appropriate messages.

    @param file_name The name of the file to be removed from the uploads table.
    
    @return The removed Uploads object if successful, or False if the file or owner is not found, 
            or if a database error occurs during the removal process.

    @exception SQLAlchemyError Logs an error message if an exception occurs during the database operation.
    """

    # Retrieve the file from the uploads table
    upload = get_file_from_uploads(file_name)
    if not upload:
        logging(f"File '{file_name}' was not found in the uploads table.")
        return False

    # Retrieve the user who owns the file
    user = get_user_from_users(upload.file_owner)
    if not user:
        logging(f"File owner '{upload.file_owner}' was not found.")
        return False

    # Attempt to remove the file from the user's record
    if not user.remove_user_file(file_name, uploads=True):
        logging(f"Failed to remove file '{file_name}' from user '{upload.file_owner}' record.")
        return False

    # Try to remove the file from the uploads table in the database
    try:
        db.session.delete(upload)
        db.session.commit()
        logging(f"File '{file_name}' successfully removed from the uploads table.")
        return upload
    except SQLAlchemyError as e:
        logging(f"An error occurred while removing file '{file_name}' from the uploads table: {e}")
        db.session.rollback()  # Rollback to undo any partial changes in case of error
        return False


def remove_file_from_db(file_name: str) -> Union[Queue, Uploads, bool]:
    """
    @brief Remove a file from the database by checking both the uploads and queue tables.

    This function first attempts to remove a file by its name from the uploads table. 
    If the file isn't found there, it then checks the queue table. If the file is found 
    in either table, it is removed from the database.

    @param file_name The name of the file to remove from the database.

    @return The removed file object (either from the uploads or queue table) if successful, 
            or False if the file isn't found in either table or an error occurs during removal.
    """

    # Attempt to remove the file from the uploads table
    upload = remove_file_from_uploads(file_name)
    if upload:
        logging(f"File '{file_name}' successfully removed from the uploads table.")
        return upload

    # If the file wasn't found in uploads, attempt to remove it from the queue table
    logging(f"File '{file_name}' not found in uploads, checking the queue table.")
    queue_file = remove_file_from_queue(file_name)
    if queue_file:
        logging(f"File '{file_name}' successfully removed from the queue table.")
        return queue_file

    # If not found in either table, log an error
    logging(f"File '{file_name}' could not be found in either the uploads or queue tables.")
    return False


def check_file_exist_in_db(file_name: str) -> bool:
    """
    @brief Check if a file exists in the uploads or queue table by file name.

    This function checks both the uploads and queue tables for the existence of a file 
    with the given name. If the file is found in either table, it logs its presence and 
    returns True. Otherwise, it returns False.

    @param file_name The name of the file to check in the database.

    @return True if the file exists in either the uploads or queue table, 
            False if the file is not found in either table.
    """

    # Check if the file exists in the queue table
    if get_file_from_queue(file_name):
        logging(f"File '{file_name}' exists in the queue table.")
        return True

    # Check if the file exists in the uploads table
    if get_file_from_uploads(file_name):
        logging(f"File '{file_name}' exists in the uploads table.")
        return True

    # If file is not found in either table, return False
    logging(f"File '{file_name}' does not exist in either the uploads or queue tables.")
    return False
