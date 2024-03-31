import os
from db_helper import get_file
from filehandler import check_file_exist, move_file
from emailhandler import sent_email_error_message


def approve_file(file_name, file_id, uploads_path:str, file_password:str):
    file_to_approve = get_file(file_name, file_id)
    if not file_to_approve:
        logging("No file or db entry approved")
        return False
    
    if not check_file_exist(file_to_approve['file_path']):
        logging(f"The requested file do not exist here: {file_to_approve.file_path}\n But a db entry for this image exist.")
        error_message = '''While trying to approve an image a database inconsistance was detected.
        The image which was requested to be approved, has a database entry but do not exist in the queue folder.'''
        sent_email_error_message("Database inconsistence", error_message)

    if file_to_approve['file_password'] != file_password:
        logging("The files password wasn't correct")
        return False

    destination_path = os.path.join(uploads_path, file_to_approve['file_name'])

    if not move_file(file_to_approve['file_path'], destination_path):
        logging("File wasn't approved")
        return False
    return True

