import unittest
import os
from tempfile import TemporaryDirectory

import sys
sys.path.append('html')
from filehandler import move_file

class TestMoveFile(unittest.TestCase):

    def test_move_file_success(self):
        # Create temporary source and destination files
        with TemporaryDirectory() as tmp_dir:
            source = os.path.join(tmp_dir, 'source.txt')
            destination = os.path.join(tmp_dir, 'destination.txt')
            with open(source, 'w') as f:
                f.write('Test content')

            # Move the file
            result = move_file(source, destination)

            # Assert that the file was moved successfully
            self.assertTrue(result)
            self.assertFalse(os.path.exists(source))
            self.assertTrue(os.path.exists(destination))

    def test_move_file_source_not_found(self):
        # Attempt to move a file that doesn't exist
        with TemporaryDirectory() as tmp_dir:
            source = os.path.join(tmp_dir, 'nonexistent.txt')
            destination = os.path.join(tmp_dir, 'destination.txt')

            # Attempt to move the file
            result = move_file(source, destination)

            # Assert that the function returns False and source file not moved
            self.assertFalse(result)
            self.assertFalse(os.path.exists(destination))

    def test_move_file_error(self):
        # Attempt to move a file to a non-existent directory
        with TemporaryDirectory() as tmp_dir:
            source = os.path.join(tmp_dir, 'source.txt')
            destination = os.path.join(tmp_dir, 'nonexistent', 'destination.txt')
            with open(source, 'w') as f:
                f.write('Test content')

            # Attempt to move the file
            result = move_file(source, destination)

            # Assert that the function returns False and source file not moved
            self.assertFalse(result)
            self.assertTrue(os.path.exists(source))
            self.assertFalse(os.path.exists(destination))
