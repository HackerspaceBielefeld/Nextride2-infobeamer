import re
import os

from PIL import Image

from helper import generate_random_string
from helper import logging
from db_helper import add_image

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


def safe_file(file, UPLOAD_FOLDER):
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    image_password = 123
    if not add_image(file.filename, image_path, image_password):
        return False
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return True