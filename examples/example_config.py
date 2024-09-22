from dimple_utils.config_utils import load_properties, get_property, get_int_property, get_bool_property, get_float_property

def main():
    # Load the properties from default and override files
    config = load_properties(default_file='test_default.properties', override_file='test_override.properties')

    # Example of retrieving a string property
    fetch_last_hours = get_property('FETCH_LAST_HOURS')
    print(f"FETCH_LAST_HOURS (String): {fetch_last_hours}")

    # Example of retrieving an integer property
    fetch_last_hours_int = get_int_property('FETCH_LAST_HOURS', fallback=24)
    print(f"FETCH_LAST_HOURS (Integer): {fetch_last_hours_int}")

    # Example of retrieving a boolean property
    enable_feature = get_bool_property('ENABLE_FEATURE', fallback=False)
    print(f"ENABLE_FEATURE (Boolean): {enable_feature}")

    # Example of retrieving a float property
    some_float = get_float_property('SOME_FLOAT', fallback=0.0)
    print(f"SOME_FLOAT (Float): {some_float}")

if __name__ == "__main__":
    main()
