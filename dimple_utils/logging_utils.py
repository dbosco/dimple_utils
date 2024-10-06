import logging
import os
import sys

def setup_logging(output_dir, log_level=logging.INFO, log_file=None, disable_file_hander = False):
    """
    Sets up the logging system to log both to a file and the console.

    :param output_dir: Directory where the log file will be saved.
    :param log_level: Optional log level (default is logging.INFO).
    :param log_file: Optional log file name. If not provided, defaults to the name of the running Python script.
    """

    # If no log file is provided, use the name of the current Python script
    if log_file is None:
        script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        log_file = f"{script_name}.log"

    # Define the log file path inside the output directory
    log_file_path = os.path.join(output_dir, log_file)

    # Get the root logger (or you can use a named logger like logging.getLogger('my_logger'))
    logger = logging.getLogger()
    logger.setLevel(log_level)  # Set the logging level for the logger

    # Remove all existing handlers
    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # # Set up logging to file and console with detailed format including filename and line number
    # logger = logging.getLogger()
    # logger.setLevel(log_level)

    # If file system is writeable, add a file handler
    # Check if file system is writeable
    if not disable_file_hander:
        try:
            # Create the output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(log_file_path, 'a'):
                    pass
        except IOError:
            disable_file_hander = True
            logging.error(f"Log file {log_file_path} is not writeable. Disabling file handler.")


    if not disable_file_hander:
        # File handler
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(log_level)  # Set the same level for the file handler
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)  # Set the same level for the console handler
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Log some initial messages to verify
    log_file_str = f"log_file: {log_file_path}" if not disable_file_hander else "log_file is disabled"
    logging.info(f"Logging initialized at level {logging.getLevelName(log_level)}. {log_file_str}")
