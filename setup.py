#!/usr/bin/env python

from os import path
from setuptools import setup, find_packages

# Helpers
def getRequirementsFromFile(filePath):
  return [l for l in open(filePath, 'rb').read().splitlines() if l and l[0] != '#']

def getRequirements():
  scriptDir = path.abspath(path.dirname(__file__))
  reqFile = 'requirements.txt'
  
  return getRequirementsFromFile(path.join(scriptDir, reqFile))

# Data
description = 'laufire - a set of utilities to help with automation'
srcDir = 'dev'

setup(
  name='laufire',
  version='0.0.3',
	package_dir={'': srcDir},
  packages=find_packages(srcDir),
  description=description,
  long_description=description,
	# url='' #ToDo: Add a URL, probablly to the corporate page or to the docs.
  author='Laufire Technologies',
  platforms='any',
  include_package_data=True,
  install_requires=getRequirements(),
	python_requires='>=2.7.10', #ToDo: Find and add the minimum required verion of python. This requires a scanning of the requirements and/or a test suite to figure out the answer.
	# dependency_links = [''], #Note: This could be helpful, in hosting a minimal package repositoty.
  license="MIT",
  zip_safe=True,
  keywords='laufire utilities automation MIT',
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Natural Language :: English',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Software Development',
    'Topic :: Utilities',
  ],
  # test_suite='', # #Note: Tests are run from ops/main.py, for simplicity.
)
