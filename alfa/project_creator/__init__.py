#!/bin/env python3
import os, os.path, shutil
from ..utils.path import CONFIG_DIR
from ..config.__internals__ import internals

class Project:

  """Creates and sets up a project, utilized in the "alfa init <dir>" command."""

  def __init__(self,path: str):
    """
    :path: root path of project. Can be relative. Can be "."

    """
    self._path = path
    abs_path = os.path.abspath(path)
    print('initializing project:',abs_path)
    self.__main__()
    print('complete')
    print('---')
    print('Please copy your credentials.json to config/credentials.json')
    pass

  def __check_can_overwrite(self,path: str):
    ''' if path exists and is not empty, ask user if overwrite. If it does not exist, it is created '''
    if not os.path.exists(path):
      os.mkdir(path)
      return True

    isempty = len(os.listdir(path))
    if isempty:
      return True

    print(os.path.abspath(path),'is not empty. Are you sure you want to overwrite?')
    choice = input('y/[n]: ')
    if len(choice) and choice[0].lower() == 'y':
      return True
    return False

  def create_folder_structure(self,conf_path: str, data_path: str):
    ''' creates the folder structure in the root directory '''
    safe_mk_root = self.__check_can_overwrite(self._path)
    if not safe_mk_root:
      return False, False, False

    safe_mk_conf = self.__check_can_overwrite(conf_path)

    safe_mk_data = self.__check_can_overwrite(data_path)

    return safe_mk_root, safe_mk_conf, safe_mk_data

  def copy_default_config(self,old_conf_path: str, new_conf_path: str):
    if os.path.exists(new_conf_path):
      return False
    shutil.copy(old_conf_path, new_conf_path)
    return True

  def __main__(self):
    root = self._path
    old_conf_path = os.path.join(CONFIG_DIR,'config.yml')
    conf_dir = os.path.join(root,internals['project']['dirs']['configs'])
    new_conf_path = os.path.join(conf_dir,internals['project']['files']['config'])
    data_path = os.path.join(root,internals['project']['dirs']['data'])
    ok_root, ok_conf, ok_data = self.create_folder_structure(conf_dir,data_path)
    if not all([ok_root, ok_conf, ok_data]):
      print('some files may have been overwritten')
    if os.path.exists(new_conf_path):
      print('config already exists, skipping copying default config')
      return True
    self.copy_default_config(old_conf_path,new_conf_path)
    return True
