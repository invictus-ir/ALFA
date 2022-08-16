#!/bin/python3
'''
helper script to aid in relative imports
'''
import os.path

def rel_path(*args: str) -> str:
  if len(args) == 1: #typically __file__
    return os.path.dirname(args[0])
  return os.path.realpath(
    os.path.join(*args)
  )

UTILS_DIR = rel_path(__file__)
ROOT_DIR = rel_path(UTILS_DIR,'..')
CONFIG_DIR = rel_path(ROOT_DIR,'config')
DATA_DIR = rel_path(ROOT_DIR,'data')