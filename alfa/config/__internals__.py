#!/bin/env/python3

import yaml
from types import SimpleNamespace
import os.path
from ..utils.path import CONFIG_DIR

with open(os.path.join(CONFIG_DIR, 'internals.yml')) as f:
  internals_dir = yaml.safe_load(f)

internals = internals_dir
