#!/usr/bin/env python2.7

from setuptools import setup, find_packages
import sys

if sys.version_info < (2, 7):
    reqs = ('ordereddict',)
else:
    reqs = tuple()

setup(
  name = 'closureidl',
  version = '0.1.1',
  description = 'Generates Closure Compiler compatible externs from IDL files.',
  author = 'Denis Zawada',
  author_email = 'oss@deno.pl',
  url = 'http://code.google.com/p/closureidl',
  download_url = 'http://code.google.com/p/closureidl/downloads/list',
  packages = find_packages('src'),
  package_dir = {'': 'src'},
  install_requires = reqs + ('appdirs>=1.2.0', 'Beaker>=1.6.3',
                      'decorator', 'requests>=0.10'),
  scripts = ['bin/closureidl'],
  classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Code Generators',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ]
)
