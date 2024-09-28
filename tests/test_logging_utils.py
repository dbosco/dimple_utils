import unittest
import os
import logging
from unittest import mock
from dimple_utils.logging_utils import setup_logging

class TestLoggingUtils(unittest.TestCase):

    def setUp(self):
        """
        Reset the logging configuration before each test.
        """
        logging.getLogger().handlers.clear()

    def tearDown(self):
        """
        Clean up after each test by shutting down the logging system.
        """
        logging.shutdown()

    @mock.patch('dimple_utils.logging_utils.os.makedirs')
    @mock.patch('dimple_utils.logging_utils.logging.FileHandler')
    @mock.patch('dimple_utils.logging_utils.logging.StreamHandler')
    @mock.patch('dimple_utils.logging_utils.logging.basicConfig')
    @mock.patch('dimple_utils.logging_utils.sys.argv', ['test_script.py'])  # Mock the script name
    def test_setup_logging_with_default_log_file(self, mock_basicConfig, mock_StreamHandler, mock_FileHandler, mock_makedirs):
        """
        Test setup_logging when no log_file is provided. It should create a log file with the script's name.
        """
        output_dir = 'logs'
        setup_logging(output_dir=output_dir)

        # Check that the directory creation is called
        mock_makedirs.assert_called_once_with(output_dir)

        # Check that the FileHandler is called with the script name log file
        expected_log_file_path = os.path.join(output_dir, 'test_script.log')
        mock_FileHandler.assert_called_once_with(expected_log_file_path)


    @mock.patch('dimple_utils.logging_utils.os.makedirs')
    @mock.patch('dimple_utils.logging_utils.logging.FileHandler')
    @mock.patch('dimple_utils.logging_utils.logging.StreamHandler')
    @mock.patch('dimple_utils.logging_utils.logging.basicConfig')
    def test_setup_logging_with_custom_log_file(self, mock_basicConfig, mock_StreamHandler, mock_FileHandler, mock_makedirs):
        """
        Test setup_logging with a custom log file.
        """
        output_dir = 'logs'
        custom_log_file = 'custom_logfile.log'

        setup_logging(output_dir=output_dir, log_file=custom_log_file)

        # Check that the directory creation is called
        mock_makedirs.assert_called_once_with(output_dir)

        # Check that the FileHandler is called with the custom log file
        expected_log_file_path = os.path.join(output_dir, custom_log_file)
        mock_FileHandler.assert_called_once_with(expected_log_file_path)


    @mock.patch('dimple_utils.logging_utils.os.makedirs')
    @mock.patch('dimple_utils.logging_utils.logging.FileHandler')
    @mock.patch('dimple_utils.logging_utils.logging.StreamHandler')
    @mock.patch('dimple_utils.logging_utils.logging.basicConfig')
    def test_setup_logging_with_custom_log_level(self, mock_basicConfig, mock_StreamHandler, mock_FileHandler, mock_makedirs):
        """
        Test setup_logging with a custom log level.
        """
        output_dir = 'logs'
        custom_log_level = logging.DEBUG

        setup_logging(output_dir=output_dir, log_level=custom_log_level)


if __name__ == '__main__':
    unittest.main()
