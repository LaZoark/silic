'''Simple demo for file configuration (via YAML)
'''
import os
from utils.params import Configuration
from utils.color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)

_CONFIG_PATH: str = os.path.join(os.getcwd(), "config")
cfg = Configuration(config_path=_CONFIG_PATH)
config: dict = cfg.read_yaml(fname="default.yaml", verbose=True)

if __name__ == "__main__":
  # logging.info(config)
  logging.info(config["version"])
  logging.info(config["api"])

