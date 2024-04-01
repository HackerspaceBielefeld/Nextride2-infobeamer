import json
import os

from flask_sqlalchemy import SQLAlchemy
from models import Uploads

from dotenv import load_dotenv

from helper import logging

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()

def check_global_upload_limit():
    try:
        # Count the number of existing entries in the database
        num_files = Uploads.query.count()

        # Check if the count exceeds the limit (100)
        if num_files >= os.environ.get('GLOBAL_UPLOAD_LIMIT'):
            logging("Maximum file limit reached. Cannot add more files.")
            return False
    except Exception as e:
        logging("Error while retrieving amount of database entries")
        return False
    return True 

def get_file(file_name: str, file_id: int):
    try:
        return Uploads.query.filter((Uploads.file_name == file_name) | (Uploads.id == file_id)).first()
    except Exception as e:
        logging(f"An error occurred while retrieving file from the database: {e}")
        return False

def add_file(file_name: str, file_path: str, file_password: str):
    try:
        upload = Uploads(file_name=file_name, file_path=file_path, file_password=file_password)
        db.session.add(upload)
        db.session.commit()
        return True
    except Exception as e:
        logging(f"An error occurred while adding file to the database: {e}")
        return False

def remove_file(file_name: str, file_id: int):
    try:
        upload = get_file(file_name, file_id)
        if upload:
            db.session.delete(upload)
            db.session.commit()
            return upload
        logging("File to delet wasn't found in the db")
        return False
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"An error occurred while removing file from the database: {e}")
        return False
    
