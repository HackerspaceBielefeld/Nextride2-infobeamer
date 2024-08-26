# pylint: skip-file

import unittest
from unittest.mock import MagicMock, patch

from io import StringIO, BytesIO
import tempfile
import sys
import os

# Ensure the 'html' directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../html')))
print(sys.path)

from filehandler import safe_file
from extensions.cms.CMSConfig import CMSConfig
from extensions.cms.CMSConfig import get_setting_from_config

class TestSafeFile(unittest.TestCase):
    
    @patch('filehandler.check_global_upload_limit', return_value=True)
    @patch('filehandler.check_file_exist_in_db', return_value=False)
    @patch('filehandler.add_file_to_queue', return_value=True)
    @patch('filehandler.sent_email_approval_request', return_value=True)
    @patch('os.path.exists', return_value=True)
    @patch('filehandler.get_setting_from_config', return_value=CMSConfig(0, "email_approve", False))
    def test_successful_safe_file(self, mock_check_global_upload_limit, 
        mock_check_file_exist_in_db, mock_add_file_to_queue, 
        mock_sent_email_approval_request, mock_os_path_exists, mock_get_setting_from_config):
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock file object
            file_mock = MagicMock()
            file_mock.filename = 'test_file.txt'
            
            # Mock file save method
            file_mock.save = MagicMock()
            
            # Call the function with the temporary directory path
            result = safe_file(file_mock, temp_dir, 'user_name')
            
            # Assertions
            self.assertTrue(result)
            # Add more assertions as needed

# Run the tests
if __name__ == '__main__':
    unittest.main()
