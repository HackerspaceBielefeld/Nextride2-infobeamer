import json

from flask_sqlalchemy import SQLAlchemy

from helper import logging

db = SQLAlchemy()

# initilize the collumns of table uploads in database
def commit_db_changes():
    # Commit the changes to the database session
    try:
        db.session.commit()
    except Exception as e:
        logging(f"Error committing changes: {e}")
        db.session.rollback()
        return False
    return True

class Uploads(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_password = db.Column(db.String(100), nullable=False)
    file_owner = db.Column(db.String(100), nullable=False)

class Queue(db.Model):
    __tablename__ = 'queue'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_password = db.Column(db.String(100), nullable=False)
    file_owner = db.Column(db.String(100), nullable=False)

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_upload_amount = db.Column(db.Integer, nullable=False)
    user_upload_limit = db.Column(db.Integer, nullable=False)
    user_role = db.Column(db.String(100), nullable=False)
    user_files_queue = db.Column(db.String)
    user_files_uploads = db.Column(db.String)

    def __init__(self, user_name, user_upload_amount, user_upload_limit, user_role, user_files):
        self.user_name = user_name
        self.user_upload_amount = user_upload_amount
        self.user_upload_limit = user_upload_limit
        self.user_role = user_role
        self.user_files_queue = json.dumps(user_files)
        self.user_files_uploads = json.dumps([])

    def get_user_files_queue(self):
        return json.loads(self.user_files_queue) if self.user_files_queue else []

    def get_user_files_uploads(self):
        return json.loads(self.user_files_uploads) if self.user_files_uploads else []

    def set_user_files(self, files:list, uploads=False):
        # Check upload is in range of the maximum user upload limit
        amount_queue = len(self.get_user_files_queue())
        amount_uploads = len(self.get_user_files_uploads())
        if uploads:
            if len(files) + amount_queue > self.user_upload_limit:
                logging("Amount of files exceeds upload limit")
                return False

            self.user_upload_amount = len(files) + amount_queue
            self.user_files_uploads = json.dumps(files)
        else:
            if len(files) + amount_uploads > self.user_upload_limit:    
                logging("Amount of files exceeds upload limit")
                return False

            self.user_upload_amount = len(files) + amount_uploads
            self.user_files_queue = json.dumps(files)

        if not commit_db_changes():
            return False
        return True

    def add_user_file(self, file:str, uploads=False):
        if self.user_upload_amount >= self.user_upload_limit:
            logging("Upload limit already reached")
            return False
        
        if uploads:
            files = self.get_user_files_uploads()
        else:
            files = self.get_user_files_queue()

        files.append(file)
        
        if not self.set_user_files(files, uploads=uploads):
            return False

        return True

    def remove_user_file(self, file:str, uploads=False):
        if uploads:
            files = self.get_user_files_uploads()
        else:
            files = self.get_user_files_queue()

        if not files:
            logging("There aren't any files to delete")
            return False

        if file not in files:
            logging("File to remove isn't present in the users files")
            return False

        files.remove(file)
        
        if not self.set_user_files(files, uploads=uploads):
            return False
            
        return True

