import os

from db_file_helper import (get_file_from_queue,add_file_to_uploads,
    remove_file_from_queue, remove_file_from_uploads)
from filehandler import move_file
from emailhandler import sent_email_error_message
from helper import logging, hash_sha_512

def approve_file(file_name, uploads_path:str, file_password:str, admin=False):
    file_to_approve = get_file_from_queue(file_name)
    file_name = file_to_approve.file_name
    file_owner = file_to_approve.file_owner
    file_path = file_to_approve.file_path

    if not file_to_approve:
        logging("No db entry for requested file, nothing approved")
        return False

    if not os.path.exists(file_path):
        logging(f"The requested file does not exist: {file_path}, "
                "but a database entry for the file exists.")
        error_message = ("While trying to approve a file, a database inconsistency was detected. "
            "The file requested to be approved has a database entry but does not "
            "exist in the queue folder.")
        sent_email_error_message("Database inconsistence", error_message)

    if not admin:
        if file_to_approve.file_password != hash_sha_512(file_password):
            logging("The files password wasn't correct")
            return False

    destination_path = os.path.join(uploads_path, file_name)
    if not add_file_to_uploads(file_name, destination_path, file_owner):
        return False

    if not remove_file_from_queue(file_name):
        logging("File couldn't be removed from the queue table -"
            "Now trying to remove it from uploads again")
        if not remove_file_from_uploads(file_name):
            logging("The file couldn't be removed from the uploads table")
            error_message = ("While trying to approve a file, it was added to the uploads table, "
                "but while removing it from the queue table, an error occurred. "
                "Trying to also remove it from the uploads table again failed.")
            sent_email_error_message("Database inconsistency", error_message)
        return False

    if not move_file(file_path, destination_path):
        logging("Moving the file from the queue to uploads went wrong - "
            "Database changes already done.")
        error_message = ("Moving an approved file failed."
            "Because the database entries were already made, "
            "the image now needs to be moved manually. Supervision is necessary to ensure "
            "this does not happen again.")
        sent_email_error_message("Database inconsistency", error_message)
        return False
    return True
