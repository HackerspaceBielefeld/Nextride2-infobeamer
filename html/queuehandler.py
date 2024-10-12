"""
@file queuehandler.py
@brief Module for handling file approval processes from the queue, including database updates and file system operations.

This module manages the approval process for files waiting in a queue. The `approve_file` function ensures that files are 
checked for existence, their passwords are verified, and they are moved to the uploads directory. The database entries 
for the file are updated accordingly. In case of inconsistencies, such as files not being found despite existing database 
records, an email alert is sent.

@details
The function `approve_file` performs the following tasks:
- Retrieves file information from the queue database.
- Checks if the file exists on disk.
- If not an admin, verifies the provided password by hashing it and comparing it with the stored hash.
- Moves the file to the uploads directory and adds it to the uploads database.
- Removes the file from the queue database.
- Handles any errors during the approval process by logging them and sending email notifications when necessary.

@dependencies
- **db_file_helper**: 
  - `get_file_from_queue`: Retrieves a file's information from the queue database.
  - `add_file_to_uploads`: Adds a file entry to the uploads database.
  - `remove_file_from_queue`: Removes a file entry from the queue database.
  - `remove_file_from_uploads`: Removes a file entry from the uploads database in case of rollback.
- **filehandler**: 
  - `move_file`: Moves the file from the queue to the uploads directory.
- **emailhandler**: 
  - `sent_email_error_message`: Sends an error notification email in case of inconsistencies or failures.
- **helper**: 
  - `logging`: Logs information and error messages.
  - `hash_sha_512`: Hashes passwords using SHA-512 for verification.
- **os**: Used for checking file existence and managing file paths.

@note
This file is part of a larger system where the approval of files is tied to database entries and file system operations. 
If a failure occurs during file approval, database consistency is handled, and alerts are sent to notify the system administrators.

@author Inflac
@date 2024
"""

import os
import logging
from typing import Union

from db_file_helper import (get_file_from_queue, 
                            add_file_to_uploads,
                            remove_file_from_queue,
                            remove_file_from_uploads)
from filehandler import move_file
from emailhandler import send_email_error_message
from helper import hash_sha_512

logger = logging.getLogger()

def approve_file(file_name: str, uploads_path: str, file_password: str, admin: bool = False) -> bool:
    """
    @brief Approve a file by verifying its existence, password, and moving it to the uploads.

    This function approves a file in the system by checking if it exists, validating its password, 
    and moving it from the queue to the uploads directory. It also updates the database 
    to reflect these changes. In case of any inconsistencies (e.g., missing file but present 
    in the database), an error email is sent.

    @param file_name The name of the file to approve.
    @param uploads_path The path to the uploads directory where the file should be moved.
    @param file_password The password provided to validate the file.
    @param admin Whether the approval is done by an admin, in which case no password check is performed.
    
    @return bool: True if the file was approved and moved successfully.
    @return bool: False if any step in the approval process failed.
    """

    # Retrieve the file from the queue.
    file_to_approve = get_file_from_queue(file_name)
    if not file_to_approve:
        logger.warning("No db entry for requested file, nothing approved")
        return False

    file_name = file_to_approve.file_name
    file_owner = file_to_approve.file_owner
    file_path = file_to_approve.file_path

    if not os.path.exists(file_path):
        logger.warning(f"The requested file does not exist: {file_path}, "
                "but a database entry for the file exists.")
        error_message = ("While trying to approve a file, a database inconsistency was detected. "
            "The file requested to be approved has a database entry but does not "
            "exist in the queue folder.")
        sent_email_error_message("Database inconsistence", error_message)
        return False

    # Check the password if not approved by an admin.
    if not admin:
        if file_to_approve.file_password != hash_sha_512(file_password):
            logger.info("The files password wasn't correct")
            return False

    # Move the file to uploads and update the database.
    destination_path = os.path.join(uploads_path, file_name)
    if not add_file_to_uploads(file_name, destination_path, file_owner):
        return False

    # Remove the file from the queue database.
    if not remove_file_from_queue(file_name):
        logger.warning("File couldn't be removed from the queue table -"
            "Now trying to remove it from uploads again")
        if not remove_file_from_uploads(file_name):
            logger.warning("The file couldn't be removed from the uploads table")
            error_message = ("While trying to approve a file, it was added to the uploads table, "
                "but while removing it from the queue table, an error occurred. "
                "Trying to also remove it from the uploads table again failed.")
            sent_email_error_message("Database inconsistency", error_message)
        return False

    # Physically move the file to the uploads folder.
    if not move_file(file_path, destination_path):
        logger.warning("Moving the file from the queue to uploads went wrong - "
            "Database changes already done.")
        error_message = ("Moving an approved file failed."
            "Because the database entries were already made, "
            "the image now needs to be moved manually. Supervision is necessary to ensure "
            "this does not happen again.")
        sent_email_error_message("Database inconsistency", error_message)
        return False
    return True
