import json
import os

from flask_sqlalchemy import SQLAlchemy
from models import Uploads

from helper import logging

db = SQLAlchemy()

def get_db_config():
    with open('config/db_config.json', 'r') as file:
        return json.load(file)

def get_db():
    with open('config/db.json', 'r') as file:
        return json.load(file)

def set_db_config(db_config):
    try:
        with open('config/db_config.json', 'w') as file:
            json.dump(db_config, file, indent=4)
    except Exception as e:
        logging(f"While writing to db_config.json an error occured: {e}")
        return False
    return True

def set_db(db_data):
    if not os.path.exists('config/db.json'):
        db_data = {"uploads": {}}

    try:
        with open('config/db.json', 'w') as file:
            json.dump(db_data, file, indent=4)
    except Exception as e:
        logging(f"While writing to db.json an error occured: {e}")
        return False
    return True


def get_lowest_free_id():
    data = get_db_config()
    return data['lowest_free_id']

def set_lowest_free_id():
    db_config = get_db_config()
    max_uploads = db_config['max_uploads']

    uploads = get_db()

    if len(uploads['uploads']) == max_uploads:
        logging(f"{len(uploads['uploads'])}/{max_uploads} uploads are stored - no more allowed")
        return False

    for i in range(max_uploads):
        if i == len(uploads['uploads']):
            db_config['lowest_free_id'] = i
            break

        elif i < uploads['uploads'][i]['id']:
            db_config['lowest_free_id'] = i
            break

    if not set_db_config(db_config):
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
    
