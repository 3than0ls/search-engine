import tomllib
import os


def load_config(config_path='./config.html'):
    """Loads configuration from a TOML file into the environment."""
    with open(config_path, 'rb') as f:
        data = tomllib.load(f)
        for key, value in data.items():
            os.environ[key] = value
