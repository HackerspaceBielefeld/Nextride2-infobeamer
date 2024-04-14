# pylint: disable=too-many-arguments
"""
Database Models Module

This module defines the database models for various tables used in the application.

Classes:
    - Uploads: Model for the 'uploads' table.
    - Queue: Model for the 'queue' table.
    - Role: Model for the 'roles' table.
    - Users: Model for the 'users' table.

Functions:
    - commit_db_changes(): Commits the changes to the database session.

Dependencies:
    - json: Provides functions for working with JSON data.
    - flask_sqlalchemy: Provides SQLAlchemy integration with Flask.
    - helper.logging: Custom logging function for error handling.

Exceptions:
    - SQLAlchemyError: Base class for all SQLAlchemy-related errors.
"""

import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from helper import logging

db = SQLAlchemy()

def commit_db_changes():
    """
    Commit the changes to the database session.

    Returns:
        bool: True if the changes were committed successfully, False otherwise.
    """
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        logging(f"Error committing changes: {e}")
        db.session.rollback()
        return False
    return True

class Uploads(db.Model):
    """
    Model for uploads table.

    Attributes:
        id (int): The primary key.
        file_name (str): The name of the file.
        file_path (str): The path to the file.
        file_owner (str): The owner of the file.
    """
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_owner = db.Column(db.String(100), nullable=False)

class Queue(db.Model):
    """
    Model for queue table.

    Attributes:
        id (int): The primary key.
        file_name (str): The name of the file.
        file_path (str): The path to the file.
        file_password (str): The password associated with the file.
        file_owner (str): The owner of the file.
    """
    __tablename__ = 'queue'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_password = db.Column(db.String(65), nullable=False)
    file_owner = db.Column(db.String(100), nullable=False)

class Role(db.Model):
    """
    Model for roles table.

    Attributes:
        id (int): The primary key.
        name (str): The name of the role.
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class Users(db.Model):
    """
    Model for users table.

    Attributes:
        id (int): The primary key.
        user_name (str): The name of the user.
        user_upload_amount (int): The number of uploads by the user.
        user_upload_limit (int): The upload limit for the user.
        user_role (Role): The role of the user.
        user_files_queue (str): JSON representation of files in the queue.
        user_files_uploads (str): JSON representation of uploaded files.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    upload_amount = db.Column(db.Integer, nullable=False)
    upload_limit = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Integer, db.ForeignKey('roles.name'))
    role = db.relationship("Role", backref="users")
    files_queue = db.Column(db.String)
    files_uploads = db.Column(db.String)

    def __init__(self, user_name, user_upload_amount, user_upload_limit, user_role, user_files):
        """
        Initialize a new User.

        Args:
            user_name (str): The name of the user.
            user_upload_amount (int): The number of uploads by the user.
            user_upload_limit (int): The upload limit for the user.
            user_role (Role): The role of the user.
            user_files (list): The list of files associated with the user.
        """
        self.name = user_name
        self.upload_amount = user_upload_amount
        self.upload_limit = user_upload_limit
        self.role = set_user_role(user_role)
        self.files_queue = json.dumps(user_files)
        self.files_uploads = json.dumps([])

    def get_user_files_queue(self):
        """
        Get the files in the user's queue.

        Returns:
            list: The list of files in the user's queue.
        """
        return json.loads(self.user_files_queue) if self.user_files_queue else []

    def get_user_files_uploads(self):
        """
        Get the files uploaded by the user.

        Returns:
            list: The list of files uploaded by the user.
        """
        return json.loads(self.user_files_uploads) if self.user_files_uploads else []

    def set_user_files(self, files:list, uploads=False):
        """
        Set the files associated with the user.

        Args:
            files (list): The list of files to associate with the user.
            uploads (bool, optional): Whether the files are uploads (default is False).

        Returns:
            bool: True if the files were set successfully, False otherwise.
        """
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
        """
        Add a file to the user's queue or uploads.

        Args:
            file (str): The file to add.
            uploads (bool, optional): Whether the file is an upload (default is False).

        Returns:
            bool: True if the file was added successfully, False otherwise.
        """
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
        """
        Remove a file from the user's queue or uploads.

        Args:
            file (str): The file to remove.
            uploads (bool, optional): Whether the file is an upload (default is False).

        Returns:
            bool: True if the file was removed successfully, False otherwise.
        """
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
        """
        Set a new role for the user.

        Args:
            new_role_name (str): The name of the new role to assign to the user.

        Returns:
            bool: True if the role was set successfully, False otherwise.
        """
        # Check if the role exists in the database
        new_role = Role.query.filter_by(name=new_role_name).first()
        if not new_role:
            logging(f"Role '{new_role_name}' does not exist.")
            return False

        # Update the user's role
        self.role = new_role

        # Commit changes to the database
        if not commit_db_changes():
            logging("Error committing changes to the database.")
            return False

        return True

def create_roles():
    # Check if the roles already exist
    existing_admin = Role.query.filter_by(name='admin').first()
    existing_default = Role.query.filter_by(name='default').first()

    # Create new roles only if they don't exist
    if not existing_admin:
        admin = Role(name='admin')
        db.session.add(admin)

    if not existing_default:
        default = Role(name='default')
        db.session.add(default)

    db.session.commit()