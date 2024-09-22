import logging
from dimple_utils.logging_utils import setup_logging

def example_logging():
    # Example 1: Setup logging with default log file (based on script name) and INFO level
    output_dir = 'logs'
    setup_logging(output_dir=output_dir)

    # Log some messages
    logging.info("This is an INFO level log message.")
    logging.debug("This DEBUG level message will not appear because the log level is INFO by default.")
    logging.error("This is an ERROR level log message.")

    # Example 2: Setup logging with a custom log file and DEBUG level
    custom_log_file = 'custom_application.log'
    setup_logging(output_dir=output_dir, log_file=custom_log_file, log_level=logging.DEBUG)

    # Log messages with different log levels
    logging.debug("This DEBUG level message will appear because the log level is DEBUG.")
    logging.info("This is another INFO level message.")
    logging.warning("This is a WARNING level message.")
    logging.error("This is an ERROR level message.")

if __name__ == '__main__':
    example_logging()
