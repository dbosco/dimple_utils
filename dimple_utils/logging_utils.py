import logging
import os
import sys

def setup_logging(output_dir, log_level=logging.INFO, log_file=None):
    """
    Sets up the logging system to log both to a file and the console.

    :param output_dir: Directory where the log file will be saved.
    :param log_level: Optional log level (default is logging.INFO).
    :param log_file: Optional log file name. If not provided, defaults to the name of the running Python script.
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # If no log file is provided, use the name of the current Python script
    if log_file is None:
        script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        log_file = f"{script_name}.log"

    # Define the log file path inside the output directory
    log_file_path = os.path.join(output_dir, log_file)

    # Set up logging to file and console with detailed format including filename and line number
    logging.basicConfig(
        level=log_level,  # Use the provided log level, default is INFO
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),   # Log to the file
            logging.StreamHandler()               # Log to the console
        ]
    )

    logging.info(f"Logging initialized at level {logging.getLevelName(log_level)}. Output directory: {output_dir}")
    logging.info(f"Logging to file: {log_file_path}")
