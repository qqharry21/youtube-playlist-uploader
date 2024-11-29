import os
import yaml
import sys


def load_config(config_path="config.yaml"):
    """
    Load configuration from a YAML file.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        dict: Configuration parameters.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    # Resolve the absolute path of the config file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    full_config_path = os.path.join(project_root, config_path)

    if not os.path.exists(full_config_path):
        print(f"Configuration file '{full_config_path}' not found.")
        sys.exit(1)

    try:
        with open(full_config_path, "r") as file:
            config = yaml.safe_load(file)
        return config
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{full_config_path}': {e}")
        sys.exit(1)


# Load configuration when the module is imported
config = load_config()
