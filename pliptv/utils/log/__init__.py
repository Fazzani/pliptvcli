import logging.config
import os

import yaml


def setup_logging(
    default_path="logging.yaml",
    default_level=os.getenv("LOG_LEVEL", logging.INFO),
    env_key="LOG_CFG",
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
        if "LOG_LEVEL" in os.environ.keys():
            config["root"]["level"] = default_level
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
