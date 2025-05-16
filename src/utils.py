import yaml
from loguru import logger

def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def setup_logging(config):
    logger.add(config["path"], level=config["level"])