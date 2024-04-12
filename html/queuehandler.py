import os

from db_file_helper import get_file_from_queue, get_file_from_uploads
from db_file_helper import add_file_to_uploads
from db_file_helper import remove_file_from_queue, remove_file_from_uploads
from filehandler import check_file_exist, move_file
from emailhandler import sent_email_error_message
from helper import logging, hash_sha_512

def approve_file(file_name, uploads_path:str, file_password:str, admin=False):
    file_to_approve = get_file_from_queue(file_name)
    if not file_to_approve:
        logging("No db entry for requested file, nothing approved")
        return False
    
    if not check_file_exist(file_to_approve.file_path):
        logging(f"The requested file do not exist here: {file_to_approve.file_path}\n But a db entry for the file exist.")
        error_message = '''While trying to approve an image a database inconsistance was detected.
        The image which was requested to be approved, has a database entry but do not exist in the queue folder.'''
        sent_email_error_message("Database inconsistence", error_message)

    if file_to_approve.file_password != hash_sha_512(file_password) and not admin:
        logging("The files password wasn't correct")
        return False

    destination_path = os.path.join(uploads_path, file_to_approve.file_name)
    if not add_file_to_uploads(file_to_approve.file_name, destination_path, file_to_approve.file_owner):
        return False
    
    if not remove_file_from_queue(file_to_approve.file_name):
        logging("File couldn't be removed from queue table - Now trying to remove it from uploads again")
        if not remove_file_from_uploads(file_to_approve.file_name, file_to_approve.id):
            logging("The file couldn't be removed from the uploads table")
            error_message = '''While trying to approve a file, it was added to the uploads table but
            while removing it from the queue table an error occured. Trying to also remove it from the
            uploads table again failed.'''
        sent_email_error_message("Database inconsistence", error_message)       
        return False

    if not move_file(file_to_approve.file_path, destination_path):
        logging("Moving the file from queue to uploads went wrong - Database changes already done.")
        error_message = '''Moving an approved file went wrong. Because the database entries were already made
        The image now needs to be moved manually. Also supervision is necessary to make sure
        this don't happen again.'''
        sent_email_error_message("Database inconsistence", error_message)       
        return False
    return True

