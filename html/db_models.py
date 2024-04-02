import json

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# initilize the collumns of table uploads in database
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


    def __init__(self, my_array):
        self.my_array = json.dumps(my_array)  # Convert array to JSON string

    def get_user_files(self):
        return json.loads(self.my_array) if self.my_array else []

    def set_user_files(self, files:list):
        if len(files) > self.user_upload_limit:
            return False
        self.user_upload_amount = len(files)
        self.my_array = json.dumps(files)

    def add_user_file(self, file:str):
        files = self.get_user_files()
        if len(files) >= self.user_upload_limit:
            return False
        files.append(file)
        self.user_upload_amount = len(files)
        self.set_array(current_array)

    def remove_user_file(self, file:str):
        files = self.get_user_files()
        if file not in files:
            return False
        files.remove(file)
        self.user_upload_amount = len(files)
        self.set_user_files(files)

