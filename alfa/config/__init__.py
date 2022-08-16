from ..utils.path import rel_path, CONFIG_DIR
import yaml, os.path

relative_config = './config/config.yml' # used when inside of a project directory
if os.path.exists(relative_config):
    config = yaml.safe_load(
            open(relative_config))
else:
    config = yaml.safe_load(
      open(rel_path(CONFIG_DIR,'config.yml'))
      )
