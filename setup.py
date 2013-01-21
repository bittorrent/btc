#!/usr/bin/env python

__author__ = 'Clement Moussu'
__author_email__ = 'clement@bittorrent.com'

from setuptools import setup, find_packages
import sys

requires = [ 'httplib2' ]

if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    requires += ['argparse', 'ordereddict']

setup(
    name = 'btc',
    version = '0.1',
    packages = find_packages(),
    author = __author__,
    author_email = __author_email__,
    description = 'command line tool for remote bittorent client control',
    install_requires = requires,
    entry_points = {
        'console_scripts': [
            'btc = btc.btc:main'
        ],
    }
)
