# pylint: skip-file

import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from unittest.mock import patch
from io import StringIO

import sys
sys.path.append('html')
from db_models import Users, db, Role

class TestUsersModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a Flask app instance
        cls.app = Flask(__name__)
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize SQLAlchemy with the Flask app
        db.init_app(cls.app)

        # Create the database tables
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Remove the database tables
        with cls.app.app_context():
            db.drop_all()

    def setUp(self):
        # Create the application context
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.session = db.session
        self.create_roles()

    def tearDown(self):
        # Remove all users from the database
        db.session.query(Users).delete()
        db.session.commit()

        # Pop the application context
        self.app_context.pop()

    def create_user(self):
        user = Users(user_name='test_user', user_upload_amount=0, user_upload_limit=10, user_files=[])
        db.session.add(user)
        db.session.commit()
        return user

    def create_roles(self):
        # Check if the roles already exist
        existing_admin = Role.query.filter_by(name='admin').first()
        existing_default = Role.query.filter_by(name='default').first()

        # Create new roles only if they don't exist
        if not existing_admin:
            admin = Role(id=9, name='admin')
            db.session.add(admin)

        if not existing_admin:
            moderator = Role(id=6, name='moderator')
            db.session.add(moderator)

        if not existing_default:
            default = Role(id=1, name='default')
            db.session.add(default)

        if not existing_default:
            block = Role(id=0, name='block')
            db.session.add(block)

        db.session.commit()

    def test_create_user(self):
        # Create a new user
        default = Role.query.filter_by(name='default').first()
        user = self.create_user()

        # Retrieve the user from the database
        retrieved_user = Users.query.filter_by(name='test_user').first()

        # Assert that the retrieved user matches the original one
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.name, 'test_user')
        self.assertEqual(retrieved_user.upload_amount, 0)
        self.assertEqual(retrieved_user.upload_limit, 10)
        self.assertEqual(retrieved_user.role, default)

    def test_get_user_files_queue(self):
        user = self.create_user()
        user_files = user.get_user_files_queue()
        self.assertEqual(user_files, [])
    
    def test_valid_add_user_file(self):
        user = self.create_user()
        example_file1 = "/home/default/images/img1.png"
        example_file2 = "/home/default/images/img2.png"
        added_file = user.add_user_file(example_file1)
        self.assertTrue(added_file)
        
        get_file = user.get_user_files_queue()
        self.assertEqual(get_file, [example_file1])
        
        added_file = user.add_user_file(example_file2, uploads=True)
        self.assertTrue(added_file)

        get_file = user.get_user_files_uploads()
        self.assertEqual(get_file, [example_file2])


    def test_upload_limit_reached_add_user_file(self):
        user = self.create_user()
        user.upload_limit = 0
        db.session.commit()

        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            example_file = "/home/default/images/img1.png"
            user_files = user.add_user_file(example_file)
            self.assertFalse(user_files)
            self.assertIn("Upload limit already reached", res_stdout.getvalue())

    def test_remove_user_file(self):
        user = self.create_user()
        example_file1 = "/home/default/images/img1.png"
        example_file2 = "/home/default/images/img2.png"
        
        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            removed_file = user.remove_user_file("test_file")
            self.assertFalse(removed_file)
            self.assertIn("There aren't any files to delete", res_stdout.getvalue())
            
        added_file = user.add_user_file(example_file1)
        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            removed_file = user.remove_user_file(example_file2)
            self.assertFalse(removed_file)
            self.assertIn("File to remove isn't present in the users files", res_stdout.getvalue())

        removed_file = user.remove_user_file(example_file1)
        self.assertTrue(removed_file)

    @patch('os.environ.get', return_value='admin1')  # Patch os.environ.get to return 'admin1'
    def test_set_user_role(self, mock_env_get):
        default = Role.query.filter_by(name='default').first()
        admin = Role.query.filter_by(name='admin').first()
        user = self.create_user()
        
        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            set_role = user.set_user_role("non_existing_role")
            self.assertFalse(set_role)
            self.assertIn("Role 'non_existing_role' does not exist.", res_stdout.getvalue())
        
        set_role = user.set_user_role("admin")
        self.assertTrue(set_role)
        self.assertEqual(user.role.name, admin.name)

        admin_user = Users(user_name='admin1', user_upload_amount=0, user_upload_limit=10, user_files=[])
        db.session.add(admin_user)
        db.session.commit()
        self.assertEqual(admin_user.role.name, default.name)
        admin_user.set_user_role("default")
        self.assertEqual(admin_user.role.name, admin.name)

if __name__ == "__main__":
    unittest.main()
