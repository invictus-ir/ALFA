#!/bin/env python3
VERSION = '0.1.0'
from setuptools import setup
import os.path
mydir = os.path.dirname(__file__)
req_path = os.path.join(mydir,'requirements.txt')
with open(req_path) as f:
    requirements = f.readlines()
setup(
    name='ALFA',
    description='',
    author='',
    packages=['alfa'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'alfa = alfa.__main__:main'
        ]
    },
    version=VERSION
)
