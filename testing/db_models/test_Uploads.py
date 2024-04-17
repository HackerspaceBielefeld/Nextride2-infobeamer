import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import sys
sys.path.append('html')
from db_models import Uploads, db

class TestUploadsModel(unittest.TestCase):
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

    def test_create_uploads_entry(self):
        # Create a sample uploads entry
        uploads_entry = Uploads(
            file_name="sample_file.txt",
            file_path="/path/to/sample_file.txt",
            file_owner="sample_owner"
        )

        # Save the uploads entry to the test database
        self.session.add(uploads_entry)
        self.session.commit()

        # Retrieve the saved uploads entry from the database
        retrieved_entry = Uploads.query.filter_by(file_name="sample_file.txt").first()

        # Assert that the retrieved entry matches the original one
        self.assertIsNotNone(retrieved_entry)
        self.assertEqual(retrieved_entry.file_name, "sample_file.txt")
        self.assertEqual(retrieved_entry.file_path, "/path/to/sample_file.txt")
        self.assertEqual(retrieved_entry.file_owner, "sample_owner")

if __name__ == "__main__":
    unittest.main()
