import yaml
import os
from utils.color_log import color
logging = color.setup(name=__name__, level=color.INFO)

class Configuration:
  def __init__(self, config_path: str) -> None:
    '''Provide a YAML parser for the configuration.
    '''
    self.path = config_path

  def read_yaml(self, fname: str='BComp.yaml', verbose: bool=True):
    """ 
    Args:
        fname: str, `'.yaml'`
            Convert YAML to `dict`
    """
    __path = os.path.join(self.path, fname)
    if os.path.exists(__path): pass
    else: logging.error(f'{__path} doesen\'t exist. Please check the "{self.path}"')
    
    with open(__path) as f:
      config = yaml.safe_load(f)
    logging.info(f'Config loaded from "{__path}"')
    if verbose:
      print(yaml.dump(config, default_flow_style=False, sort_keys=False))
    return config

  def dict2yaml(self, config: dict, fname: str='example.yaml', save: bool=True, overwrite: bool=False):
    """ Convert `dict` to YAML and save the yaml to `fname`. 
    It is useful to save the configuration to yaml. \n
    Args:
        config: dict, hyperparameters
        fname: str, filename
        save: bool, optional (default=True)
            whether to output the config to a YAML
        overwrite: bool, optional (default=False)
            allowing the `<fname>` to be overwrote
    """
    if save:
      __path = os.path.join(self.path, fname)
      if os.path.exists(__path):
        if not overwrite:
          raise Exception(f'"{__path}" already exists! \nIf you want to overwirte the yaml, please set "overwrite=True"')
        else: logging.warning(f'"{__path}" already exists. Overwriting the YAML...')
      else: pass
        
      with open(__path, 'w') as f:
        yaml.dump(config, stream=f, default_flow_style=False, sort_keys=False)
      with open(__path, 'r') as f:
        logging.info(f'Saved to "{__path}".')
        print(f'{"="*30}\n{f.read()}{"="*30}')
    else:
      converted = yaml.dump(config, default_flow_style=False, sort_keys=False)
      print(converted)
