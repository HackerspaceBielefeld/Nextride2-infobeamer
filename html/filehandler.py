import re
import os

from PIL import Image

from helper import generate_random_string
from helper import logging
from db_helper import add_image, remove_image
from emailer import sent_email_approval_request

def sanitize_filename(filename:str):
    pattern = r'a-zA-Z0-9_\-.' # RE pattern with whitelisted chars 
    sanitized_filename = re.sub(f'[^{pattern}]', "", filename) # Replace chars that aren't whitelisted
    sanitized_filename_extended = generate_random_string(8) + "_" + sanitized_filename # Extend the sanitized filename with random chars to avoid colissions
    return sanitized_filename_extended

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


def safe_file(file, QUEUE_FOLDER):
    image_path = os.path.join(QUEUE_FOLDER, file.filename)
    image_password = 123
    
    if not add_image(file.filename, image_path, image_password):
        return False
    
    file_path = os.path.join(QUEUE_FOLDER, file.filename)
    file.save(file_path)

    if not sent_email_approval_request(file_path):
        return False
    return True


def delete_file(image_name=None, image_id=None):
    if not image_name and not image_id:
        logging("Tried to remove an image but no image name or id was provided")
        return False

    file_data = remove_image(image_name, image_id)
    if not file_data: return False
    
    file_path = file_data['image_path']

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