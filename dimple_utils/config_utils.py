import os
import logging
import dotenv
from typing import Dict, Any, Optional

config = None
secret_config = None

def _parse_properties_file(file_path: str) -> Dict[str, str]:
    """
    Parse a simple properties file with name=value format.
    
    :param file_path: Path to the properties file
    :return: Dictionary of key-value pairs
    """
    properties = {}
    if not os.path.exists(file_path):
        return properties
        
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    properties[key] = value
                else:
                    print(f"Warning: Invalid line format in {file_path} at line {line_num}: {line}")
                    logging.warning(f"Invalid line format in {file_path} at line {line_num}: {line}")
    except Exception as e:
        print(f"Error reading properties file {file_path}: {e}")
        logging.error(f"Error reading properties file {file_path}: {e}")
        raise
    
    return properties

def load_properties(default_file: str = 'default.properties', override_file: str = None, secrets_file: str = None) -> Dict[str, str]:
    """
    Loads global variables from default, override, and optionally a secrets file using simple name=value format.

    :param default_file: Path to the default properties file.
    :param override_file: Path to the override properties file (can be passed as input or via environment variable).
    :param secrets_file: Path to the secrets properties file (optional).
    :return: Dictionary of loaded configuration (excluding secrets).
    """
    global config, secret_config
    config = {}
    secret_config = {}
    abs_default_file = os.path.abspath(default_file)

    # Load default properties
    try:
        dotenv.load_dotenv()

        # Check if the file exists
        default_file_exists = os.path.exists(abs_default_file)
        print(f"Default properties file: {abs_default_file}. Exists: {default_file_exists}")
        if default_file_exists:
            config = _parse_properties_file(abs_default_file)
            print(f"Default properties loaded from {abs_default_file}")
            print_properties("Before override")
        else:
            print(f"Default configuration is mandatory. Please provide a valid default.properties file. Property file location: {abs_default_file}")
            logging.error(f"Default configuration is mandatory. Please provide a valid default.properties file. Property file location: {abs_default_file}")
            raise FileNotFoundError(f"Default configuration is mandatory. Please provide a valid default.properties file. Property file location: {abs_default_file}")
    except Exception as e:
        print(f"Error loading default properties {abs_default_file}: {e}")
        logging.error(f"Error loading default properties {abs_default_file}: {e}")
        raise

    # Check if override file is passed via input or environment variable
    if override_file is None:
        override_file = os.getenv('OVERRIDE_FILE')

    # Load override properties (excluding secrets)
    if override_file and os.path.exists(override_file):
        override_props = _parse_properties_file(override_file)
        config.update(override_props)
        print(f"Override properties loaded from {override_file}")
        print_properties("After override")
    elif override_file:
        print(f"Override file {override_file} not found. Using default properties only.")
        logging.warning(f"Override file {override_file} not found. Using default properties only.")
    else:
        print("No override file found. Using default properties only.")
        logging.warning("No override file found. Using default properties only.")

    # Print all the configurations
    print(f"[BEGIN] Printing current configurations (before loading env and secrets):")
    logging.info(f" [BEGIN] Printing current configurations (before loading env and secrets):")
    for key, value in config.items():
        print(f"  {key} = {value}")
        logging.info(f"  {key} = {value}")
    print(f"[DONE] Printing current configurations (before loading env and secrets).")
    logging.info(f" [DONE] Printing current configurations (before loading env and secrets).")

    # Let's load the environment variables. Environment variables will override the properties file
    # Get all the environment variables
    env_vars = os.environ
    for key in env_vars:
        value = env_vars[key]
        if "$" in value:
            # With $ python gives exception
            continue
        # Replace _dot_ with . in the key
        key = key.replace("_dot_", ".")
        config[key] = value
        print(f"Set {key} from environment variables")

    # Load secrets file (optional)
    if secrets_file and os.path.exists(secrets_file):
        secrets_props = _parse_properties_file(secrets_file)
        
        # Separate secrets from regular properties
        for key, value in secrets_props.items():
            if key.upper().startswith('SECRET_') or 'SECRET' in key.upper():
                secret_config[key] = value
            else:
                print(f"Overriding {key} with value {value} from secrets file {secrets_file}")
                config[key] = value

        print(f"Secrets properties loaded from {secrets_file}")
        logging.info(f"Secrets properties loaded from {secrets_file}")
        print_properties("After loading secrets")
    elif secrets_file:
        print(f"Secrets file {secrets_file} not found.")
        logging.warning(f"Secrets file {secrets_file} not found.")

    return config

def get_secret(key: str, section: str = "SECRETS") -> str:
    """
    Retrieve a secret from the secret_config.

    :param key: The key to retrieve from the secret_config.
    :param section: The section in the secret_config. Default is "SECRETS".
    :return: The secret value or None if not found.
    """
    if secret_config and key in secret_config:
        return secret_config[key]
    else:
        logging.warning(f"Secret key '{key}' not found.")
        return None

def print_properties(debug_string: str):
    """
    Prints all properties in the configuration.
    :param debug_string: A string to differentiate the output (e.g., "Before override", "After override")
    """
    print(f"\n--- {debug_string} ---")
    logging.info(f"--- {debug_string} ---")

    if config:
        print("Configuration properties:")
        for key, value in config.items():
            print(f"  {key} = {value}")
            logging.info(f"  {key} = {value}")
    else:
        print("No configuration properties found.")
        logging.info("No configuration properties found.")


def set_property(key: str, value: str, section: str = 'DEFAULT'):
    """
    Set a property value in the configuration object.
    :param key: The property key
    :param value: The property value
    :param section: The section (for compatibility, not used in simple format)
    :return: None
    """
    if config is not None:
        config[key] = value

def get_property(key: str, section: str = 'DEFAULT', fallback: any = None) -> str:
    """
    Get a property value as a string from the configuration with an optional fallback.

    :param key: The property key to retrieve.
    :param section: The section (for compatibility, not used in simple format).
    :param fallback: Fallback value if the property is not found.
    :return: The property value as a string or fallback.
    """
    if config is not None and key in config:
        return config[key]
    return fallback

def get_int_property(key: str, section: str = 'DEFAULT', fallback: int = 0) -> int:
    """
    Get a property value as an integer from the configuration with an optional fallback.

    :param key: The property key to retrieve.
    :param section: The section (for compatibility, not used in simple format).
    :param fallback: Fallback value if the property is not found.
    :return: The property value as an integer or fallback.
    """
    if config is not None and key in config:
        try:
            return int(config[key])
        except ValueError:
            logging.warning(f"Could not convert property '{key}' to integer: {config[key]}")
            return fallback
    return fallback

def get_bool_property(key: str, section: str = 'DEFAULT', fallback: bool = False) -> bool:
    """
    Get a property value as a boolean from the configuration with an optional fallback.

    :param key: The property key to retrieve.
    :param section: The section (for compatibility, not used in simple format).
    :param fallback: Fallback value if the property is not found.
    :return: The property value as a boolean or fallback.
    """
    if config is not None and key in config:
        value = config[key].lower()
        if value in ('true', '1', 'yes', 'on'):
            return True
        elif value in ('false', '0', 'no', 'off'):
            return False
        else:
            logging.warning(f"Could not convert property '{key}' to boolean: {config[key]}")
            return fallback
    return fallback

def get_float_property(key: str, section: str = 'DEFAULT', fallback: float = 0.0) -> float:
    """
    Get a property value as a float from the configuration with an optional fallback.

    :param key: The property key to retrieve.
    :param section: The section (for compatibility, not used in simple format).
    :param fallback: Fallback value if the property is not found.
    :return: The property value as a float or fallback.
    """
    if config is not None and key in config:
        try:
            return float(config[key])
        except ValueError:
            logging.warning(f"Could not convert property '{key}' to float: {config[key]}")
            return fallback
    return fallback
