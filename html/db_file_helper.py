import json
import os

from flask_sqlalchemy import SQLAlchemy
from db_models import Uploads, Queue, db

from dotenv import load_dotenv

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
    except Exception as e:
        logging(f"Error while retrieving amount of database entries:\n{e}")
        return False
    return True 

def get_file_from_queue(file_name: str):
    try:
        return db.session.query(Queue).filter(Queue.file_name == file_name).first()
    except Exception as e:
        logging(f"An error occurred while retrieving file from the queue table: {e}")
        return False

def add_file_to_queue(file_name: str, file_path: str, file_password: str):
    try:
        upload = Queue(file_name=file_name, file_path=file_path, file_password=file_password)
        db.session.add(upload)
        db.session.commit()
        return True
    except Exception as e:
        logging(f"An error occurred while adding file to the queue table: {e}")
        return False

def remove_file_from_queue(file_name: str):
    try:
        upload = get_file_from_queue(file_name)
        if upload:
            db.session.delete(upload)
            db.session.commit()
            return upload
        logging("File to delete wasn't found in the queue table")
        return False
    except Exception as e:
        print(f"An error occurred while removing file from the queue table: {e}")
        return False


def get_file_from_uploads(file_name: str):
    try:
        return db.session.query(Uploads).filter(Uploads.file_name == file_name).first()
    except Exception as e:
        logging(f"An error occurred while retrieving file from the uploads table: {e}")
        return False

def add_file_to_uploads(file_name: str, file_path: str, file_password: str):
    try:
        upload = Uploads(file_name=file_name, file_path=file_path, file_password=file_password)
        db.session.add(upload)
        db.session.commit()
        return True
    except Exception as e:
        logging(f"An error occurred while adding file to the uploads table: {e}")
        return False

def remove_file_from_uploads(file_name: str):
    try:
        upload = get_file_from_uploads(file_name)
        if upload:
            db.session.delete(upload)
            db.session.commit()
            return upload
        logging("File to delete wasn't found in the uploads table")
        return False
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"An error occurred while removing file from the uploads table: {e}")
        return False
    
