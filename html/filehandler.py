import shutil
import re
import os

from PIL import Image

from helper import generate_random_string, generate_secret_token
from helper import logging
from db_file_helper import check_global_upload_limit
from db_file_helper import remove_file_from_queue, remove_file_from_uploads
from db_file_helper import add_file_to_queue
from db_user_helper import get_user_from_users
from emailhandler import sent_email_approval_request

def sanitize_filename(file_name:str):
    pattern = r'a-zA-Z0-9_\-.' # RE pattern with whitelisted chars 
    sanitized_filename = re.sub(f'[^{pattern}]', "", file_name) # Replace chars that aren't whitelisted
    sanitized_filename_extended = generate_random_string(8) + "_" + sanitized_filename # Extend the sanitized filename with random chars to avoid colissions
    return sanitized_filename_extended

def check_file_exist(file_path:str):
    return os.path.exists(file_path)

def move_file(source:str, destination:str):
    try:
        shutil.move(source, destination)
        logging(f"File moved from {source} to {destination}")
        return True
    except Exception as e:
        logging(f"Error while moving a file: {e}")
        return False

def check_image(file):
    # Check the file extension
    if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ['jpg', 'jpeg', 'png', 'gif']:
        logging("File extension is not allowed")
        return False

    # Check if the file is actually an image
    try:
        img = Image.open(file)
        img.verify()  # Attempt to open and verify the image file
        return True
    except:
        logging("Uploaded file isn't an image")
    return False

def sanitize_file(file, MAX_CONTENT_LENGTH):
    if not file:
        logging("Upload pressed but no file was selected")
        return False

    if not len(file.read()) <= MAX_CONTENT_LENGTH:
        logging(f"Uploaded file is to big: {len(file.read())}")
        return False
    file.seek(0)

    file.filename = sanitize_filename(file.filename)

    if not check_image(file):
        logging("Uploaded file isn't an image or the extension is not allowed")    
        return False
    file.seek(0)

    return file


def safe_file(file, QUEUE_FOLDER, user_name):
    if not check_global_upload_limit():
        logging('Global upload limit restricted the upload')
        return False

    user = get_user_from_users(user_name)
    if user.user_upload_amount == user.user_upload_limit:
        logging('Personal upload limit restricted the upload')
        return False

    file_path = os.path.join(QUEUE_FOLDER, file.filename)
    file_password = generate_secret_token()
    
    if not add_file_to_queue(file.filename, file_path, file_password):
        logging("File wasn't saved in the queue because no db entry could be created")
        return False

    try:
        file.save(file_path)
    except Exception as e:
        logging("file couldn't be saved")
        if not remove_file_from_queue(file.filename, None):
            logging("DB entry couldn't be removed for unsaved file")
        return False
    
    if not sent_email_approval_request(file.filename, file_password, file_path):
        logging("Failed to sent a file approval email")
        return False
    
    if not user.add_user_file(file.filename):
        logging("Failed adding file to users db")
    return True
    

def delete_file(file_name:str):
    file_data = remove_file_from_db(file_name, None)
    if not file_data: return False
    
    file_path = file_data['file_path']

    try:
        os.remove(file_path)
        logging(f"File '{file_path}' deleted successfully.")
        return True
    except FileNotFoundError:
        logging(f"File '{file_path}' not found.")
    except PermissionError:
        logging(f"Permission denied to delete file '{file_path}'.")
    except Exception as e:
        logging(f"An error occurred while deleting file '{file_path}': {e}")
    return False