import unittest
from unittest import mock
import os
import configparser
from dimple_utils.config_utils import load_properties, get_property, get_int_property, get_bool_property, get_float_property, get_secret

class TestConfigUtils(unittest.TestCase):

    @mock.patch('dimple_utils.config_utils.os.getenv', return_value=None)
    @mock.patch('dimple_utils.config_utils.configparser.ConfigParser.read')
    def test_load_properties_default(self, mock_read, mock_getenv):
        """
        Test loading default properties without an override or secrets file.
        """
        config = load_properties(default_file='test_default.properties')

        mock_read.assert_called_once_with('test_default.properties')


    @mock.patch('dimple_utils.config_utils.os.getenv', return_value=None)  # Ensure no OVERRIDE_FILE environment variable
    @mock.patch('dimple_utils.config_utils.os.path.exists', return_value=False)  # Simulate that override file doesn't exist
    @mock.patch('dimple_utils.config_utils.configparser.ConfigParser.read')
    def test_load_properties_no_override(self, mock_read, mock_path_exists, mock_getenv):
        """
        Test loading properties when the override file is not found.
        """
        config = load_properties(default_file='test_default.properties')

        # Ensure the default file is read
        mock_read.assert_called_once_with('test_default.properties')



    @mock.patch('dimple_utils.config_utils.configparser.ConfigParser')
    def test_get_property(self, MockConfigParser):
        """
        Test retrieving a string property.
        """
        mock_config = MockConfigParser.return_value
        mock_config.has_option.return_value = True
        mock_config.get.return_value = '24'

        load_properties(default_file='test_default.properties')
        value = get_property('FETCH_LAST_HOURS', fallback='48')

        self.assertEqual(value, '24')

    @mock.patch('dimple_utils.config_utils.configparser.ConfigParser')
    def test_get_int_property(self, MockConfigParser):
        """
        Test retrieving an integer property.
        """
        mock_config = MockConfigParser.return_value
        mock_config.has_option.return_value = True
        mock_config.getint.return_value = 24

        load_properties(default_file='test_default.properties')
        value = get_int_property('FETCH_LAST_HOURS', fallback=48)

        self.assertEqual(value, 24)

    @mock.patch('dimple_utils.config_utils.configparser.ConfigParser')
    def test_get_bool_property(self, MockConfigParser):
        """
        Test retrieving a boolean property.
        """
        mock_config = MockConfigParser.return_value
        mock_config.has_option.return_value = True
        mock_config.getboolean.return_value = True

        load_properties(default_file='test_default.properties')
        value = get_bool_property('ENABLE_FEATURE', fallback=False)

        self.assertTrue(value)

    @mock.patch('dimple_utils.config_utils.configparser.ConfigParser')
    def test_get_float_property(self, MockConfigParser):
        """
        Test retrieving a float property.
        """
        mock_config = MockConfigParser.return_value
        mock_config.has_option.return_value = True
        mock_config.getfloat.return_value = 12.5

        load_properties(default_file='test_default.properties')
        value = get_float_property('SOME_FLOAT', fallback=0.0)

        self.assertEqual(value, 12.5)

    @mock.patch('dimple_utils.config_utils.os.path.exists', return_value=True)
    @mock.patch('dimple_utils.config_utils.configparser.ConfigParser.read')
    def test_load_properties_with_secrets(self, mock_read, mock_path_exists):
        """
        Test loading properties with a secrets file.
        """
        config = load_properties(default_file='test_default.properties', secrets_file='secrets.properties')

        # Ensure default and secrets files were read
        mock_read.assert_any_call('test_default.properties')
        mock_read.assert_any_call('secrets.properties')

    @mock.patch('dimple_utils.config_utils.secret_config')
    def test_get_secret(self, mock_secret_config):
        """
        Test retrieving a secret from the secret_config.
        """
        mock_secret_config.has_option.return_value = True
        mock_secret_config.get.return_value = 'supersecret'

        # Test retrieval of secret
        secret_value = get_secret('API_KEY')

        self.assertEqual(secret_value, 'supersecret')
        mock_secret_config.has_option.assert_called_once_with('SECRETS', 'API_KEY')
        mock_secret_config.get.assert_called_once_with('SECRETS', 'API_KEY')

    @mock.patch('dimple_utils.config_utils.secret_config')
    def test_get_secret_missing(self, mock_secret_config):
        """
        Test retrieving a non-existent secret.
        """
        mock_secret_config.has_option.return_value = False

        # Test that the secret is not found
        secret_value = get_secret('NON_EXISTENT_KEY')

        self.assertIsNone(secret_value)
        mock_secret_config.has_option.assert_called_once_with('SECRETS', 'NON_EXISTENT_KEY')

if __name__ == '__main__':
    unittest.main()
