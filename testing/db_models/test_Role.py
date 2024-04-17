import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import sys
sys.path.append('html')
from db_models import Role, db

class TestRoleModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a Flask app instance for testing
        cls.app = Flask(__name__)
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize SQLAlchemy with the Flask app
        db.init_app(cls.app)

        # Create all tables in the in-memory SQLite database
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Remove the tables after testing
        with cls.app.app_context():
            db.drop_all()

    def setUp(self):
        # Create a new database session for each test
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.session = db.session

    def tearDown(self):
        # Rollback the session after each test to discard any changes
        self.session.rollback()
        self.app_context.pop()

    def test_create_role_entry(self):
        # Create a sample role entry
        role_entry = Role(
            id=1,
            name="default"
        )

        # Save the role entry to the test database
        self.session.add(role_entry)
        self.session.commit()

        # Retrieve the saved role entry from the database
        retrieved_entry = Role.query.filter_by(name="default").first()

        # Assert that the retrieved entry matches the original one
        self.assertIsNotNone(retrieved_entry)
        self.assertEqual(retrieved_entry.name, "default")
        self.assertEqual(retrieved_entry.id, 1)

if __name__ == "__main__":
    unittest.main()
