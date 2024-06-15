import os

from db_models import Uploads, Queue, db

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from db_user_helper import get_user_from_users
from helper import logging

# Load environment variables from .env file
load_dotenv()

def check_global_upload_limit():
    try:
        # Count the number of existing entries in the database
        num_files = Uploads.query.count()

        # Check if the count exceeds the limit (100)
        if num_files >= int(os.environ.get('GLOBAL_UPLOAD_LIMIT')):
            logging("Maximum file limit reached. Cannot add more files.")
            return False
    except SQLAlchemyError as e:
        logging(f"Error while retrieving amount of database entries:\n{e}")
        return False
    return True

def get_file_from_queue(file_name: str):
    try:
        return db.session.query(Queue).filter(Queue.file_name == file_name).first()
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving file from the queue table: {e}")
        return False

def add_file_to_queue(file_name: str, file_path: str, file_password: str, file_owner: str):
    user = get_user_from_users(file_owner)
    if not user:
        logging("File owner couldn't be found")
        return False

    if not user.add_user_file(file_name, uploads=False):
        logging("Failed adding file to users table")
        return False

    try:
        upload = Queue(file_name=file_name, file_path=file_path,
            file_password=file_password, file_owner=file_owner)
        db.session.add(upload)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        logging(f"An error occurred while adding file to the queue table: {e}")
        return False

def remove_file_from_queue(file_name: str):
    upload = get_file_from_queue(file_name)
    if not upload:
        logging("File to delete wasn't found in the queue table")
        return False

    # Get user and delete the file from the queue table
    user = get_user_from_users(upload.file_owner)
    if not user:
        logging("File owner couldn't be found")
        return False

    if not user.remove_user_file(file_name, uploads=False):
        logging("Failed removing file from queue db")
        return False

    try:
        db.session.delete(upload)
        db.session.commit()
        return upload
    except SQLAlchemyError as e:
        logging(f"An error occurred while removing file from the queue table: {e}")
        return False


def get_file_from_uploads(file_name: str):
    try:
        return db.session.query(Uploads).filter(Uploads.file_name == file_name).first()
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving file from the uploads table: {e}")
        return False

def add_file_to_uploads(file_name: str, file_path: str, file_owner: str):
    user = get_user_from_users(file_owner)
    if not user:
        logging("File owner couldn't be found")
        return False

    if not user.add_user_file(file_name, uploads=True):
        logging("Failed adding file to users table")
        return False

    try:
        upload = Uploads(file_name=file_name, file_path=file_path, file_owner=file_owner)
        db.session.add(upload)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        logging(f"An error occurred while adding file to the uploads table: {e}")
        return False

def remove_file_from_uploads(file_name: str):
    upload = get_file_from_uploads(file_name)
    if not upload:
        logging("File to delete wasn't found in the uploads table")
        return False

    # Get user and delete the file from the users table
    user = get_user_from_users(upload.file_owner)
    if not user:
        logging("File owner couldn't be found")
        return False

    if not user.remove_user_file(file_name, uploads=True):
        logging("Failed removing file from users db")
        return False

    try:
        db.session.delete(upload)
        db.session.commit()
        return upload
    except SQLAlchemyError as e:
        logging(f"An error occurred while removing file from the uploads table: {e}")
        return False

def remove_file_from_db(file_name: str):
    upload = remove_file_from_uploads(file_name)
    if not upload:
        upload = remove_file_from_queue(file_name)
        if not upload:
            logging("File couldn't be removed from db")
            return False
    return upload


def check_file_exist_in_db(file_name:str):
    if get_file_from_queue(file_name):
        logging(f"File {file_name} exist in queue")
        return True
    if get_file_from_uploads(file_name):
        logging(f"File {file_name} exist in uploads")
        return True
    return False
