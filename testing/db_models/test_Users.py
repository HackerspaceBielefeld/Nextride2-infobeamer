import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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
        user = Users(user_name='test_user', user_upload_amount=0, user_upload_limit=10, user_files=[])
        db.session.add(user)
        db.session.commit()

        # Retrieve the user from the database
        retrieved_user = Users.query.filter_by(name='test_user').first()

        # Assert that the retrieved user matches the original one
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.name, 'test_user')
        self.assertEqual(retrieved_user.upload_amount, 0)
        self.assertEqual(retrieved_user.upload_limit, 10)
        self.assertEqual(retrieved_user.role, default)

if __name__ == "__main__":
    unittest.main()
