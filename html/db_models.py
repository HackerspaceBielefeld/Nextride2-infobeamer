# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes

import json
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from helper import logging

db = SQLAlchemy()

def commit_db_changes():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        logging(f"Error committing changes: {e}")
        db.session.rollback()
        return False
    return True

class Uploads(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_owner = db.Column(db.String(100), nullable=False)

class Queue(db.Model):
    __tablename__ = 'queue'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_password = db.Column(db.String(65), nullable=False)
    file_owner = db.Column(db.String(100), nullable=False)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

def create_roles():
    # Check if the roles already exist
    existing_admin = Role.query.filter_by(name='admin').first()
    existing_moderator = Role.query.filter_by(name='moderator').first()
    existing_default = Role.query.filter_by(name='default').first()
    existing_block = Role.query.filter_by(name='block').first()    

    # Create new roles only if they don't exist
    if not existing_admin:
        admin = Role(id=9, name='admin')
        db.session.add(admin)

    if not existing_moderator:
        moderator = Role(id=6, name='moderator')
        db.session.add(moderator)

    if not existing_default:
        default = Role(id=1, name='default')
        db.session.add(default)

    if not existing_block:
        block = Role(id=0, name='block')
        db.session.add(block)

    db.session.commit()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    upload_amount = db.Column(db.Integer, nullable=False)
    upload_limit = db.Column(db.Integer, nullable=False)
    role_name = db.Column(db.Integer, db.ForeignKey('roles.name'))
    role = db.relationship("Role", backref="users")
    files_queue = db.Column(db.String)
    files_uploads = db.Column(db.String)

    def __init__(self, user_name, user_upload_amount, user_upload_limit, user_files):
        self.name = user_name
        self.upload_amount = user_upload_amount
        self.upload_limit = user_upload_limit
        self.role = Role.query.filter_by(name='default').first()
        self.files_queue = json.dumps(user_files)
        self.files_uploads = json.dumps(user_files)

    def get_user_files_queue(self):
        return json.loads(self.files_queue) if self.files_queue else []

    def get_user_files_uploads(self):
        return json.loads(self.files_uploads) if self.files_uploads else []

    def set_user_files(self, files:list, uploads=False):
        amount_queue = len(self.get_user_files_queue())
        amount_uploads = len(self.get_user_files_uploads())
        if uploads:
            if len(files) + amount_queue > self.upload_limit:
                logging("Amount of files exceeds upload limit")
                return False

            self.upload_amount = len(files) + amount_queue
            self.files_uploads = json.dumps(files)
        else:
            if len(files) + amount_uploads > self.upload_limit:
                logging("Amount of files exceeds upload limit")
                return False

            self.upload_amount = len(files) + amount_uploads
            self.files_queue = json.dumps(files)

        if not commit_db_changes():
            return False
        return True

    def add_user_file(self, file:str, uploads=False):
        if self.upload_amount >= self.upload_limit:
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

    def set_user_role(self, new_role_name: str):
        # Check if the role exists in the database
        new_role = Role.query.filter_by(name=new_role_name).first()

        admin_users = os.environ.get('ADMIN_USERS').split(',')
        if self.name in admin_users:
            new_role = Role.query.filter_by(name="admin").first()

        if not new_role:
            logging(f"Role '{new_role_name}' does not exist.")
            return False

        # Update the user's role
        self.role = new_role

        # Commit changes to the database
        if not commit_db_changes():
            return False

        return True

    def set_user_upload_limit(self, new_upload_limit: int):
        if not new_upload_limit >=0:
            return False

        self.upload_limit = new_upload_limit

        if not commit_db_changes():
            return False
        return True

def create_users():
    # Check if the user already exist
    existing_system = Role.query.filter_by(name='system').first()    

    # Create new roles only if they don't exist
    if not existing_system:
        system = Users(user_name='system', user_upload_amount=0, user_upload_limit=10000000, user_files=[])
        db.session.add(system)

### Extension ###
class Extension(db.Model):
    __tablename__ = 'extension'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    managable = db.Column(db.Boolean, nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def activate(self):
        self.active = True

        if not commit_db_changes():
            return False
        return True
    
    def deactivate(self):
        self.active = False

        if not commit_db_changes():
            return False
        return True


def create_extensions():
    # Itterate over the extensions folder to add them to the extension table
    for extension_name in os.listdir("extensions"):
        extension_elem = Extension.query.filter_by(name=extension_name).first()    

        if not extension_elem:
            if "templates" in os.listdir(os.path.join("extensions", extension_name)):
                extension_elem = Extension(name=extension_name, managable=True, active=False)
            else:
                extension_elem = Extension(name=extension_name, managable=False, active=False)
            db.session.add(extension_elem)
            db.session.commit()
