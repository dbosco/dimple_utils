import unittest
from unittest import mock
import requests
from dimple_utils.request_utils import request_get_with_retry, create_session

class TestRequestUtils(unittest.TestCase):

    @mock.patch('dimple_utils.request_utils.requests.get')
    def test_request_get_with_retry_success(self, mock_get):
        """
        Test successful GET request without any retries.
        """
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = request_get_with_retry('https://example.com', max_retries=5)

        # Ensure that the request was made once with no retries
        mock_get.assert_called_once_with('https://example.com')
        self.assertEqual(response.status_code, 200)

    @mock.patch('dimple_utils.request_utils.time.sleep', return_value=None)  # To skip actual sleep during test
    @mock.patch('dimple_utils.request_utils.requests.get')
    def test_request_get_with_retry_throttling(self, mock_get, mock_sleep):
        """
        Test retry logic when throttled (status code 429).
        """
        mock_response = mock.Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '10'}
        mock_get.return_value = mock_response

        response = request_get_with_retry('https://example.com', max_retries=3)

        # Ensure that the request was retried the maximum number of times
        self.assertEqual(mock_get.call_count, 3)
        mock_sleep.assert_called_with(10)

    @mock.patch('dimple_utils.request_utils.time.sleep', return_value=None)  # To skip actual sleep during test
    @mock.patch('dimple_utils.request_utils.requests.get')
    def test_request_get_with_retry_default_wait_time(self, mock_get, mock_sleep):
        """
        Test retry logic when there is an error and no Retry-After header is provided.
        """
        mock_response = mock.Mock()
        mock_response.status_code = 429
        mock_response.headers = {}
        mock_get.return_value = mock_response

        response = request_get_with_retry('https://example.com', max_retries=2)

        # Ensure that the default wait time of 30 seconds is used when Retry-After is not provided
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_with(30)

    @mock.patch('dimple_utils.request_utils.time.sleep', return_value=None)  # Skip sleep
    @mock.patch('dimple_utils.request_utils.requests.get')
    def test_request_get_with_retry_custom_wait_time(self, mock_get, mock_sleep):
        """
        Test retry logic with a custom wait time between retries.
        """
        mock_response = mock.Mock()
        mock_response.status_code = 500  # Simulate server error
        mock_get.return_value = mock_response

        response = request_get_with_retry('https://example.com', max_retries=2, wait_time=15)

        # Ensure the custom wait time of 15 seconds is used
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_with(15)

    @mock.patch('dimple_utils.request_utils.time.sleep', return_value=None)  # Skip sleep
    @mock.patch('dimple_utils.request_utils.requests.get')
    def test_request_get_with_retry_zero_retries(self, mock_get, mock_sleep):
        """
        Test that no retries are made when max_retries is set to 0.
        """
        mock_response = mock.Mock()
        mock_response.status_code = 500  # Simulate server error
        mock_get.return_value = mock_response

        response = request_get_with_retry('https://example.com', max_retries=0)

        # Ensure the request is only made once with no retries
        mock_get.assert_called_once_with('https://example.com')
        self.assertEqual(mock_get.call_count, 1)
        mock_sleep.assert_not_called()

    @mock.patch('dimple_utils.request_utils.requests.Session')
    def test_create_session(self, mock_session):
        """
        Test creating a session with user and password.
        """
        user = 'test_user'
        password = 'test_password'

        session = create_session(user, password)

        # Ensure that a session was created with basic authentication
        mock_session.return_value.auth = (user, password)
        mock_session.assert_called_once()

if __name__ == '__main__':
    unittest.main()
