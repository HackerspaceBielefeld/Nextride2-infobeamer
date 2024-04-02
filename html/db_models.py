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

class Queue(db.Model):
    __tablename__ = 'queue'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_password = db.Column(db.String(100), nullable=False)

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_upload_amount = db.Column(db.Integer, nullable=False)
    user_upload_limit = db.Column(db.Integer, nullable=False)
    user_role = db.Column(db.String(100), nullable=False)
    user_files = db.Column(db.String)  # Storing the array as a string

    def __init__(self, user_name, user_upload_amount, user_upload_limit, user_role, user_files):
        self.user_name = user_name
        self.user_upload_amount = user_upload_amount
        self.user_upload_limit = user_upload_limit
        self.user_role = user_role
        self.user_files = json.dumps(user_files)  # Convert array to JSON string

    def get_user_files(self):
        return json.loads(self.user_files) if self.user_files else []

    def set_user_files(self, files:list):
        if len(files) > self.user_upload_limit:
            return False

        self.user_upload_amount = len(files)
        self.user_files = json.dumps(files)

        if not commit_db_changes():
            return False
        return True

    def add_user_file(self, file:str):
        files = self.get_user_files()
        if len(files) >= self.user_upload_limit:
            return False
        
        files.append(file)
        self.user_upload_amount = len(files)
        
        if not self.set_user_files(files):
            return False

        if not commit_db_changes():
            return False
        return True

    def remove_user_file(self, file:str):
        files = self.get_user_files()
        if file not in files:
            return False

        files.remove(file)
        self.user_upload_amount = len(files)
        
        if not self.set_user_files(files):
            return False

        if not commit_db_changes():
            return False
        return True

