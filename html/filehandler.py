"""
File Management Module

This module provides functions for file management, including file sanitization,
file existence checks, file movement, image validation, file upload handling, and file deletion.

Functions:
    - sanitize_filename(file_name): Sanitizes a file name by removing disallowed characters
        and adding random prefixes.
    - move_file(source, destination): Moves a file from the source path to the destination path.
    - check_image(file): Checks if the uploaded file is an image with an accepted extension.
    - sanitize_file(file, MAX_CONTENT_LENGTH): Sanitizes an uploaded file
        before further processing.
    - safe_file(file, QUEUE_FOLDER, user_name): Safely handles the upload of
        a file to the queue folder.
    - delete_file(file_name): Deletes a file from the filesystem and
        its corresponding entry from the database.

Dependencies:
    - shutil: Provides functions for file operations.
    - os: Provides functions for interacting with the operating system.
    - PIL: Python Imaging Library for image processing.
"""

import shutil
import os

from PIL import Image

from helper import generate_random_string, generate_secret_token, sanitize_string
from helper import logging, hash_sha_512
from db_file_helper import check_global_upload_limit
from db_file_helper import remove_file_from_queue, remove_file_from_db
from db_file_helper import add_file_to_queue
from db_file_helper import check_file_exist_in_db
from db_models import Users
from emailhandler import sent_email_approval_request

def sanitize_filename(file_name:str):
    sanitized_filename = sanitize_string(file_name)

    # Extend the sanitized filename with random chars to avoid colissions
    sanitized_filename_extended = generate_random_string(8) + "_" + sanitized_filename
    return sanitized_filename_extended

def move_file(source: str, destination: str):
    """
    Move a file from the source path to the destination path.

    Args:
        source (str): The path of the source file.
        destination (str): The path of the destination file.

    Returns:
        bool: True if the file was moved successfully, False otherwise.

    Raises:
        FileNotFoundError: If the source file cannot be found.
        shutil.Error: If an error occurs while moving the file.
    """
    try:
        shutil.move(source, destination)
        logging(f"File moved from {source} to {destination}")
        return True
    except FileNotFoundError as e:
        logging(f"Error: Source file '{source}' not found: {e}")
    except shutil.Error as e:
        logging(f"Error: Failed to move file from '{source}' to '{destination}': {e}")
    return False

def check_image(file):
    """
    Checks if the uploaded file is an image and has an accepted file extension.

    This function checks the file extension and attempts to open and verify the image file.

    Args:
        file: The uploaded file object.

    Returns:
        bool: True if the file is an image and has an accepted extension, False otherwise.
    """

    # Check the file extension
    if not '.' in file.filename:
        logging("File extension not present")
        return False
    if file.filename.rsplit('.', 1)[1].lower() not in ['jpg', 'jpeg', 'png', 'gif']:
        logging("File extension not accepted")
        return False

    # Check if the file is actually an image
    try:
        img = Image.open(file)
        img.verify()  # Attempt to open and verify the image file
        return True
    except FileNotFoundError as e:
        logging(f"Error: File not found: {e}")
    except Image.UnidentifiedImageError as e:
        logging(f"Error: Unidentified image: {e}")
    except ValueError as e:
        logging(f"Error: Invalid mode or file pointer: {e}")
    except TypeError as e:
        logging(f"Error: Invalid format types: {e}")
    return False

def sanitize_file(file, MAX_CONTENT_LENGTH):
    """
    Sanitizes an uploaded file.

    This function performs several checks and sanitization steps
    on an uploaded file before further processing:
    * It checks the file size to be smaler than a maximum content length.
    * The filenmae is sanitized
    * The fileextensio is checked against a whitelist
    * It's tested if the image can be opened to verify it's content is actually the one of an image

    Args:
        file: The uploaded file object.
        MAX_CONTENT_LENGTH (int): The maximum allowed content length for the file.

    Returns:
        file or False: The sanitized file object if it passes all checks, False otherwise.
    """

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
    """
    Safely handles the upload of a file to the queue folder.

    This function checks various conditions before saving the file
    to ensure a safe and successful upload process.
    
    Args:
        file (FileStorage): The file object to be saved.
        QUEUE_FOLDER (str): The path to the queue folder where the file will be stored.
        user_name (str): The name of the user performing the upload.

    Returns:
        bool: True if the file was successfully saved and
        an email approval request was sent, False otherwise.

    Raises:
        FileNotFoundError: If the specified file path does not exist.
        IsADirectoryError: If the specified file path points to a directory instead of a file.
        PermissionError: If permission is denied while attempting to save the file.
    """

    if not check_global_upload_limit():
        logging('Global upload limit restricted the upload')
        return False

    if check_file_exist_in_db(file.filename):
        logging("A file with the same name is already in the db")
        return False

    file_path = os.path.join(QUEUE_FOLDER, file.filename)
    file_password = generate_secret_token()
    file_password_hashed = hash_sha_512(file_password)

    if not add_file_to_queue(file.filename, file_path, file_password_hashed, user_name):
        logging("File wasn't saved in the queue because no db entry could be created")
        return False

    try:
        file.save(file_path)
        if not sent_email_approval_request(file.filename, file_password, file_path):
            logging("Failed to sent a file approval email")
            return False
        return True

    except FileNotFoundError:
        logging("The specified file path does not exist")
    except IsADirectoryError:
        logging("The specified file path is a directory")
    except PermissionError:
        logging("Permission denied while attempting to save the file")

    if not remove_file_from_queue(file.filename):
        logging("DB entry couldn't be removed for unsaved file")
    return False


def delete_file(file_name:str):
    """
    Deletes a file from the filesystem and its corresponding entry from the database.

    This function attempts to delete the specified file
    from the filesystem and its corresponding entry from the database.
    
    Args:
        file_name (str): The name of the file to be deleted.

    Returns:
        bool: True if the file was successfully deleted, False otherwise.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If permission is denied to delete the file.
    """

    file_data = remove_file_from_db(file_name)
    if not file_data:
        logging("Fileremove_file_from_db couldn't be removed from database")
        return False

    file_path = file_data.file_path

    try:
        os.remove(file_path)
        logging(f"File '{file_path}' deleted successfully.")
        return True
    except FileNotFoundError:
        logging(f"File '{file_path}' not found.")
    except PermissionError:
        logging(f"Permission denied to delete file '{file_path}'.")
    return False


def get_all_images_for_all_users():
    all_images = {}
    all_users = Users.query.all()

    for user in all_users:
        username = user.name
        queue_images = user.get_user_files_queue()
        upload_images = user.get_user_files_uploads()
        all_images[username] = {'queue': queue_images, 'uploads': upload_images}

    return all_images
