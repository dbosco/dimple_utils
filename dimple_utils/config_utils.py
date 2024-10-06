import configparser
import os
import logging

config = None
secret_config = None

def load_properties(default_file: str = 'default.properties', override_file: str = None, secrets_file: str = None) -> configparser.ConfigParser:
    """
    Loads global variables from default, override, and optionally a secrets file.

    :param default_file: Path to the default properties file.
    :param override_file: Path to the override properties file (can be passed as input or via environment variable).
    :param secrets_file: Path to the secrets properties file (optional).
    :return: Loaded configuration object (excluding secrets).
    """
    global config, secret_config
    config = configparser.ConfigParser()
    secret_config = configparser.ConfigParser()

    # Load default properties
    try:
        print(f"Default properties file: {os.path.abspath(default_file)}")
        config.read(default_file)
        print(f"Default properties loaded from {default_file}")
        print_properties("Before override")

    except FileNotFoundError as e:
        print(f"Default file {default_file} not found: {e}")
        logging.error(f"Default file {default_file} not found: {e}")
        raise

    # Check if override file is passed via input or environment variable
    if override_file is None:
        override_file = os.getenv('OVERRIDE_FILE')

    # Load override properties (excluding secrets)
    if override_file and os.path.exists(override_file):
        config.read(override_file)
        print(f"Override properties loaded from {override_file}")
        print_properties("After override")
    elif override_file:
        print(f"Override file {override_file} not found. Using default properties only.")
        logging.warning(f"Override file {override_file} not found. Using default properties only.")
    else:
        print("No override file found. Using default properties only.")
        logging.warning("No override file found. Using default properties only.")

    # Let's load the environment variables. Environment variables will override the properties file
    # Get all the environment variables
    env_vars = os.environ
    for key in env_vars:
        # Replace _dot_ with . in the key
        key = key.replace("_dot_", ".")
        config.set("DEFAULT", key, env_vars[key])
        print(f"Set {key} from environment variables")

    # Load secrets file (optional)
    if secrets_file and os.path.exists(secrets_file):
        temp_config = configparser.ConfigParser()
        temp_config.read(secrets_file)

        # Move SECRETS section to secret_config
        if "SECRETS" in temp_config.sections():
            secret_config.add_section("SECRETS")
            for key, value in temp_config.items("SECRETS"):
                secret_config.set("SECRETS", key, value)

        # Copy other sections to the main config (excluding SECRETS)
        for section in temp_config.sections():
            if section != "SECRETS":
                if not config.has_section(section):
                    config.add_section(section)
                for key, value in temp_config.items(section):
                    config.set(section, key, value)

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
    if secret_config.has_option(section, key):
        return secret_config.get(section, key)
    else:
        logging.warning(f"Secret key '{key}' not found in section '{section}'.")
        return None

def print_properties(debug_string: str):
    """
    Prints only the keys of properties explicitly defined in each section.
    :param debug_string: A string to differentiate the output (e.g., "Before override", "After override")
    """
    print(f"\n--- {debug_string} ---")
    logging.info(f"--- {debug_string} ---")

    # Print keys in the DEFAULT section
    if config.defaults():
        print("Keys in DEFAULT section:")
        for key in config.defaults():
            print(f"  {key}")
        logging.info(f"Keys in DEFAULT section: {list(config.defaults().keys())}")

    # Print keys in each section, excluding keys inherited from DEFAULT
    for section in config.sections():
        print(f"Explicit keys in section '{section}':")
        section_keys = config.options(section)
        default_keys = config.defaults().keys()

        # Filter out the keys that are present in DEFAULT
        explicit_keys = [key for key in section_keys if key not in default_keys]

        for key in explicit_keys:
            print(f"  {key}")
        logging.info(f"Explicit keys in section '{section}': {explicit_keys}")


def set_property(key: str, value: str, section: str = 'DEFAULT'):
    """
    Set a property value in the configuration object.
    :param key:
    :param value:
    :param section:
    :return:
    """
    config.set(section, key, value)

def get_property(key: str, section: str = 'DEFAULT', fallback: any = None) -> str:
    """
    Get a property value as a string from a given section with an optional fallback.

    :param key: The property key to retrieve.
    :param section: The section in the configuration file. Defaults to 'DEFAULT'.
    :param fallback: Fallback value if the property is not found.
    :return: The property value as a string or fallback.
    """
    return config.get(section, key, fallback=fallback)

def get_int_property(key: str, section: str = 'DEFAULT', fallback: int = 0) -> int:
    """
    Get a property value as an integer from a given section with an optional fallback.

    :param key: The property key to retrieve.
    :param section: The section in the configuration file. Defaults to 'DEFAULT'.
    :param fallback: Fallback value if the property is not found.
    :return: The property value as an integer or fallback.
    """
    return config.getint(section, key, fallback=fallback)

def get_bool_property(key: str, section: str = 'DEFAULT', fallback: bool = False) -> bool:
    """
    Get a property value as a boolean from a given section with an optional fallback.

    :param key: The property key to retrieve.
    :param section: The section in the configuration file. Defaults to 'DEFAULT'.
    :param fallback: Fallback value if the property is not found.
    :return: The property value as a boolean or fallback.
    """
    return config.getboolean(section, key, fallback=fallback)

def get_float_property(key: str, section: str = 'DEFAULT', fallback: float = 0.0) -> float:
    """
    Get a property value as a float from a given section with an optional fallback.

    :param key: The property key to retrieve.
    :param section: The section in the configuration file. Defaults to 'DEFAULT'.
    :param fallback: Fallback value if the property is not found.
    :return: The property value as a float or fallback.
    """
    return config.getfloat(section, key, fallback=fallback)
