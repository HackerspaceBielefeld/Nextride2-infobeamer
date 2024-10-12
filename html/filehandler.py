"""
@file file_management.py
@brief This module provides functions for managing files, including sanitization, validation, uploading, and deletion.

This module supports operations like sanitizing filenames, moving files, verifying image files,
handling file uploads, and removing files from both the filesystem and the database. It includes
logging and integrates with other services like email approval requests.

Dependencies:
    - shutil: Provides functions for file operations.
    - os: Provides functions for interacting with the operating system.
    - PIL: Python Imaging Library for image processing.
    - helper: Custom helper functions for generating secure random strings,
        string sanitization, hashing, and file path management.
    - db_file_helper: Helper functions for interacting with the database regarding file operations.
    - emailhandler: Sends approval request emails for file uploads.

@author Inflac
@date 2024
"""

import os
import io
import shutil
import logging

from typing import Union
from PIL import Image

from helper import (generate_random,
                    sanitize_string,
                    hash_sha_512,
                    get_file_path)
from db_file_helper import check_global_upload_limit
from db_file_helper import remove_file_from_queue, remove_file_from_db
from db_file_helper import add_file_to_queue
from db_file_helper import check_file_exist_in_db
from db_models import Users
from emailhandler import send_email_approval_request

from extensions.cms.CMSConfig import get_setting_from_config

logger = logging.getLogger()


def sanitize_filename(file_name:str) -> str:
    """
    @brief Sanitizes a filename and adds a random 8-character prefix.

    @param file_name The unsanitized filename.

    @return The sanitized filename with a random 8-character prefix added.
    """

    sanitized_filename = sanitize_string(file_name)

    # Extend the sanitized filename with random chars to avoid colissions
    sanitized_filename_extended = generate_random(length=8) + "_" + sanitized_filename
    return sanitized_filename_extended

def move_file(source:str, destination:str) -> bool:
    """
    @brief Moves a file from the source path to the destination path.

    @param source The path of the source file.
    @param destination The path of the destination file.

    @return True if the file was moved successfully, False otherwise.

    @exception FileNotFoundError Logs an error message if the source file cannot be found.
    @exception PermissionError Logs an error if the file cannot be moved due to permission issues.
    @exception OSError Logs any other errors that occur during the file move operation.
    """

    try:
        shutil.move(source, destination)
        logger.debug(f"File moved from {source} to {destination}")
        return True
    except FileNotFoundError as e:
        logger.error(f"Error: Source file '{source}' not found: {e}")
    except PermissionError as e:
        logger.error(f"Permission error while moving file '{source}': {e}")
    except OSError as e:
        logger.error(f"Error moving file '{source}': {e}")
    return False

def check_image(file) -> bool:
    """
    @brief Checks if the uploaded file is an image and has an accepted extension.

    This function verifies both the file extension and the image file's validity.

    @param file The uploaded file object.

    @return True if the file is a valid image with an accepted extension, False otherwise.

    @exception FileNotFoundError Logs an error if the image file is not found.
    @exception PIL.UnidentifiedImageError Logs an error if the file is not a recognized image.
    @exception ValueError Logs an error if the file cannot be opened.
    @exception TypeError Logs an error if the file is of the wrong type.
    """

    # Check the file extension
    if not '.' in file.filename:
        logger.info("File extension not present")
        return False
    if file.filename.rsplit('.', 1)[1].lower() not in ['jpg', 'jpeg', 'png', 'gif']:
        logger.info("File extension not accepted")
        return False

    # Check if the file is actually an image
    try:
        img = Image.open(file)
        img.verify()  # Attempt to open and verify the image file
        return True
    except (FileNotFoundError, Image.UnidentifiedImageError, ValueError, TypeError) as e:
        logger.error(f"Error while checking an image: {e}")
    return False

def sanitize_file(file, MAX_CONTENT_LENGTH:int) -> Union[io.TextIOWrapper, bool]:
    """
    @brief Sanitizes an uploaded file and checks its validity.

    This function sanitizes the filename, verifies the file size, and checks if it is a valid image.

    @param file The uploaded file object.
    @param MAX_CONTENT_LENGTH The maximum allowed content length.

    @return The sanitized file object if all checks pass, otherwise False.
    """

    if not file:
        logger.info("No file within the request")
        return False

    if not len(file.read()) <= MAX_CONTENT_LENGTH:
        logger.info(f"Uploaded file is to big: {len(file.read())}")
        return False
    file.seek(0)

    file.filename = sanitize_filename(file.filename)

    if not check_image(file):
        logger.info("Uploaded file isn't an image or the extension is not allowed")
        return False
    file.seek(0)

    return file


def safe_file(file, QUEUE_FOLDER:str, user_name:str) -> bool:
    """
    @brief Handles the safe upload of a file to the queue folder.

    This function checks upload limits, ensures the filename doesn't already exist, and initiates
    the file saving process with additional features like password hashing and email approval requests.

    @param file The file to be uploaded.
    @param QUEUE_FOLDER The path to the queue folder where the file will be saved.
    @param user_name The name of the user performing the upload.

    @return True if the file was successfully saved and an approval email was sent, False otherwise.

    @exception FileNotFoundError Logs an error if the specified file path does not exist.
    @exception IsADirectoryError Logs an error if the specified file path points to a directory.
    @exception PermissionError Logs an error if permission is denied while attempting to save the file.
    """

    if not check_global_upload_limit():
        logger.info('Global upload limit restricted the upload')
        return False

    if check_file_exist_in_db(file.filename):
        logger.info("A file with the same name is already in the db")
        return False

    file_path = get_file_path(QUEUE_FOLDER, file.filename)
    if not file_path:
        logger.warning("An error occured while crafting the path where to safe the file")
        return False

    file_password = generate_random()
    file_password_hashed = hash_sha_512(file_password)

    if not add_file_to_queue(file.filename, file_path, file_password_hashed, user_name):
        logger.warning("File wasn't saved in the queue because no db entry could be created")
        return False

    try:
        file.save(file_path)

        email_setting = get_setting_from_config("email_approve")
        if not email_setting.active:
            return True

        if not sent_email_approval_request(file.filename, file_password, file_path):
            logger.warning("Failed to sent a file approval email")
            return False
        return True

    except FileNotFoundError:
        logger.error("The specified file path does not exist")
    except IsADirectoryError:
        logger.error("The specified file path is a directory")
    except PermissionError:
        logger.error("Permission denied while attempting to save the file")

    if not remove_file_from_queue(file.filename):
        logger.warning("DB entry couldn't be removed for unsaved file")
    return False


def delete_file(file_name:str) -> bool:
    """
    @brief Deletes a file from the filesystem and its entry from the database.

    This function attempts to remove the specified file from both the filesystem and the database.

    @param file_name The name of the file to be deleted.

    @return True if the file was successfully deleted, False otherwise.

    @exception FileNotFoundError Logs an error if the specified file does not exist.
    @exception PermissionError Logs an error if permission is denied to delete the file.
    """

    file_data = remove_file_from_db(file_name)
    if not file_data:
        logger.warning(f"File {file_name} couldn't be removed from database")
        return False

    file_path = file_data.file_path

    try:
        os.remove(file_path)
        logger.debug(f"File '{file_path}' deleted successfully.")
        return True
    except FileNotFoundError:
        logger.error(f"File '{file_path}' not found.")
    except PermissionError:
        logger.error(f"Permission denied to delete file '{file_path}'.")
    return False


def get_all_images_for_all_users(queue_only=False) -> dict[str, dict[str, list[str]]]:
    """
    @brief Retrieves all queued and uploaded images for all users.

    This function fetches all users from the database and gathers their queued and uploaded images.
    If `queue_only` is set to True, only the images in the queue will be retrieved.

    @param queue_only A boolean flag indicating whether to return only queued images.
    
    @return A dictionary where the keys are usernames, and the values are dictionaries
            with the user's queued and uploaded images.

    @exception SQLAlchemyError Logs an error message if a database query fails.
    @exception KeyError Logs if there are any issues accessing user information.
    """

    all_images = {}
    try:
        all_users = Users.query.all()
        logger.debug(f"Retrieved {len(all_users)} users from the database.")
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while retrieving users: {e}")
        return all_images

    for user in all_users:
        username = user.name
        queue_images = user.get_user_files_queue()

        if queue_only:
            all_images[username] = {'queue': queue_images}
            continue

        upload_images = user.get_user_files_uploads()
        all_images[username] = {'queue': queue_images, 'uploads': upload_images}

    return all_images

def get_uploads(upload_folder:str, extensions_folder:str) -> tuple[list[str], dict[str, list[str]]]:
    """
    @brief Retrieves uploaded images and categorizes them based on file extensions.

    This function scans the upload folder for images and categorizes them by their extension.
    Images with recognized extensions are added to the `extension_images` dictionary,
    while others are placed in the `uploaded_images` list.

    @param upload_folder The directory where uploaded images are stored.
    @param extensions_folder The directory where allowed extensions are listed.

    @return A tuple containing:
        - uploaded_images: A list of image filenames that do not match any known extension.
        - extension_images: A dictionary where keys are extensions and values are lists of image filenames.

    @exception FileNotFoundError Logs an error if the upload or extensions folder is not found.
    @exception OSError Logs any issues that arise during file system access.
    """

    extension_images = {}
    uploaded_images = []

    extensions = os.listdir(extensions_folder)
    files = os.listdir(upload_folder)

    try:
        extensions = os.listdir(extensions_folder)
        files = os.listdir(upload_folder)
    except FileNotFoundError as e:
        logger.error(f"Folder not found: {e}")
        return uploaded_images, extension_images
    except OSError as e:
        logger.error(f"Error accessing file system: {e}")
        return uploaded_images,     

    for file in files:
        if os.path.isfile(os.path.join(upload_folder, file)):
            extension = file.split("_", 1)[0]
            if extension in extensions:
                if extension not in extension_images:
                    extension_images[extension] = []
                extension_images[extension].append(file)
            else:
                uploaded_images.append(file)

    return uploaded_images, extension_images
