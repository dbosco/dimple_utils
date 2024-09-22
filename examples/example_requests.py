import logging
from unittest import mock
from dimple_utils.request_utils import request_get_with_retry, create_session
from dimple_utils.logging_utils import setup_logging

# Mock response data for simulating the external server response
mock_response_data = {
    "userId": 1,
    "id": 1,
    "title": "Mock Title",
    "body": "This is mock response data."
}

def example_request_without_session():
    """
    Example of making a GET request without a session using request_get_with_retry, with mocked responses.
    """
    full_url = 'https://mockurl.com/posts/1'

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Mock requests.get to return a successful response without hitting the actual server
    with mock.patch('requests.get') as mock_get:
        # Create a mock response object
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

        # Call the function with the mock in place
        response = request_get_with_retry(full_url, max_retries=3, wait_time=15)

        if response and response.status_code == 200:
            logging.info("Mock request successful. Response data:")
            logging.info(response.json())  # Print mock JSON response data
        else:
            logging.error(f"Failed to fetch mock data. Status code: {response.status_code if response else 'No response'}")

def example_request_with_session():
    """
    Example of making a GET request with a session using request_get_with_retry, with mocked responses.
    """
    full_url = 'https://mockurl.com/posts/2'
    user = 'test_user'
    password = 'test_password'

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create a session with basic authentication
    session = create_session(user, password)

    # Mock session.get to return a successful response without hitting the actual server
    with mock.patch.object(session, 'get') as mock_session_get:
        # Create a mock response object
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_session_get.return_value = mock_response

        # Call the function with the mock in place
        response = request_get_with_retry(full_url, max_retries=5, session=session, wait_time=10)

        if response and response.status_code == 200:
            logging.info("Mock request with session successful. Response data:")
            logging.info(response.json())  # Print mock JSON response data
        else:
            logging.error(f"Failed to fetch mock data with session. Status code: {response.status_code if response else 'No response'}")


if __name__ == '__main__':

    output_dir = 'logs'
    setup_logging(output_dir=output_dir)

    logging.info("Starting request examples without session...")
    example_request_without_session()

    logging.info("Starting request examples with session...")
    example_request_with_session()
