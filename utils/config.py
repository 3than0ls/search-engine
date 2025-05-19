import tomllib
import os


def load_config(config_path='./config.toml') -> None:
    """Loads configuration from a TOML file into the environment."""
    with open(config_path, 'rb') as f:
        data = tomllib.load(f)
        for _, configs in data.items():
            for key, value in configs.items():
                if os.environ.get(key) is None:
                    os.environ[key] = value
