import logging
import time
import traceback
import requests

def request_get_with_retry(full_url, max_retries=5, session=None, wait_time=30):
    """
    Makes a GET request with retry logic.

    :param full_url: The full URL for the GET request.
    :param max_retries: The maximum number of retries (default is 5). If 0, it will not retry.
    :param session: An optional requests session object (if not provided, a new request will be made without session).
    :param wait_time: The time to wait between retries in case of failure (default is 30 seconds).
    :return: The response object from the GET request.
    """
    retry_count = 0
    response = None

    while retry_count < max_retries or (max_retries == 0 and retry_count == 0):
        try:
            # Make the request using the session if provided, otherwise use the default requests.get
            if session:
                response = session.get(full_url)
            else:
                response = requests.get(full_url)

            # If throttled, handle Retry-After header
            if response.status_code == 429:  # Throttled
                retry_after = int(response.headers.get('Retry-After', wait_time))
                logging.warning(f"Throttled. status_code={response.status_code}."
                                f" Retrying after {retry_after} seconds. retry_count={retry_count}")
                time.sleep(retry_after)
                retry_count += 1
            elif response.status_code >= 200 and response.status_code < 500:  # Success
                break
            else:
                logging.error(f"Error: {response.status_code}. Retrying... retry_count={retry_count}")
                if max_retries > 0:
                    logging.warning(f"Error response. status_code={response.status_code}."
                                    f" Retrying after {wait_time} seconds. retry_count={retry_count}")
                    time.sleep(wait_time)
                retry_count += 1

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            logging.error(traceback.format_exc())
            if retry_count == 0:  # If no retries, wait before trying again
                logging.info(f"Waiting for {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            retry_count += 1

    return response


def create_session(user, password):
    """
    Creates a requests session with basic authentication.

    :param user: Username for authentication.
    :param password: Password for authentication.
    :return: A configured requests session object.
    """
    session = requests.Session()
    session.auth = (user, password)
    return session
