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

def get_file(file_name:str, file_id:int):
    db_data = get_db()
    
    for file in db_data['uploads']:
        if file['file_name'] == file_name or file['id'] == file_id:
            return file
    logging("The requested file couldn't be found in the database")
    return None

def add_file(file_name:str, file_path:str, file_password):
    lowest_free_id = get_lowest_free_id()

    upload_info = {
        "id": lowest_free_id,
        "file_name": file_name,
        "file_path": file_path,
        "file_password": file_password
    }

    db_data = get_db()

    # Add the new upload information to the uploads dictionary
    #if lowest_free_id == 0:
    db_data["uploads"].insert(lowest_free_id, upload_info)

    # Save the updated data back to db.json
    if not set_db(db_data):
        return False

    if not set_lowest_free_id():
        return False

    logging(f"Upload information for ID {lowest_free_id} has been saved to db.json.")
    return True

def remove_file(file_name, file_id):
    file_to_remove = get_file(file_name, file_id)
    if not file_to_remove:
        logging("No file or db entry removed")
        return False

    db_data = get_db()
    db_data["uploads"].remove(file_to_remove)
    if not set_db(db_data):
        logging("No file or db entry removed")
        return False

    if not set_lowest_free_id():
        logging("Couldn't set lowest free id but db entry was already removed")
        return False
    
    return db_data
    