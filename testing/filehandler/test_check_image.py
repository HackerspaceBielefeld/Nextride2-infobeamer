# pylint: skip-file

import unittest
from unittest.mock import MagicMock, patch

from io import StringIO, BytesIO

import sys
sys.path.append('html')
from filehandler import check_image

class TestCheckImage(unittest.TestCase):
    valid_file_data = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0d\x49\x44\x41\x54\x08\x5b\x63\x08\xb4\xfb\xf5\x1f\x00\x04\xf6\x02\x89\x64\xca\x2e\xd6\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"
    invalid_file_data = b"\x89\x50\x4e\x47\x00\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0d\x49\x44\x41\x54\x08\x5b\x63\x08\xb4\xfb\xf5\x1f\x00\x04\xf6\x02\x89\x64\xca\x2e\xd6\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

    def test_valid_image(self):
        file_object = BytesIO(self.valid_file_data)
        setattr(file_object, 'filename', 'image.png')  # Mimic the filename attribute
        result = check_image(file_object)
        self.assertTrue(result)

    def test_file_extension_not_accepted(self):
        file_object = BytesIO(self.valid_file_data)
        setattr(file_object, 'filename', 'image.js')

        # Patch sys.stdout to capture printed output
        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            result = check_image(file_object)
            self.assertFalse(result)
            self.assertIn("File extension not accepted", res_stdout.getvalue())

    def test_file_extension_not_present(self):
        file_object = BytesIO(self.valid_file_data)
        setattr(file_object, 'filename', 'imagejs')

        # Patch sys.stdout to capture printed output
        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            result = check_image(file_object)
            self.assertFalse(result)
            self.assertIn("File extension not present", res_stdout.getvalue())

    def test_invalid_image(self):
        file_object = BytesIO(self.invalid_file_data)
        setattr(file_object, 'filename', 'image.png')  # Mimic the filename attribute
        
        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            result = check_image(file_object)
            self.assertFalse(result)
            self.assertIn("Error: Unidentified image:", res_stdout.getvalue())
