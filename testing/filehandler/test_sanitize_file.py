import unittest
from unittest.mock import MagicMock, patch

from io import StringIO, BytesIO
from werkzeug.datastructures import FileStorage

import sys
sys.path.append('html')
from filehandler import sanitize_file

class TestSanitizeFile(unittest.TestCase):
    valid_file_data = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0d\x49\x44\x41\x54\x08\x5b\x63\x08\xb4\xfb\xf5\x1f\x00\x04\xf6\x02\x89\x64\xca\x2e\xd6\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"
    invalid_file_data = b"\x89\x50\x4e\x47\x00\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0d\x49\x44\x41\x54\x08\x5b\x63\x08\xb4\xfb\xf5\x1f\x00\x04\xf6\x02\x89\x64\xca\x2e\xd6\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"


    def test_valid_file(self):
        file_object = BytesIO(self.valid_file_data)
        setattr(file_object, 'filename', 'image.png')  # Mimic the filename attribute
        result = sanitize_file(file_object, 100)
        self.assertEqual(result, file_object)

    def test_no_file_selected(self):
        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            result = sanitize_file(None, 100)
            self.assertFalse(result)
            self.assertIn("Upload pressed but no file was selected", res_stdout.getvalue())

    def test_file_too_big(self):
        file_object = BytesIO(self.valid_file_data)
        setattr(file_object, 'filename', 'image.png')

        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            result = sanitize_file(file_object, 10)
            self.assertFalse(result)
            self.assertIn("Uploaded file is to big:", res_stdout.getvalue())
    
    def test_invalid_file(self):
        file_object = BytesIO(self.invalid_file_data)
        setattr(file_object, 'filename', 'image.png')  # Mimic the filename attribute
        
        with patch('sys.stdout', new_callable=StringIO) as res_stdout:
            result = sanitize_file(file_object, 100)
            self.assertFalse(result)
            self.assertIn("Error: Unidentified image:", res_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()