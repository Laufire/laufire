r"""
OS Bridge
=========

A multi platform adapter.
"""
import os
import platform

from os.path import expanduser

# Data
platform = platform.system()

def getOSRoot():
	return '' if platform != 'Windows' else os.environ['windir'][:2] # #Note: An empty string is returned, as it's the projets standard to always join the paths with a separator.

def getDataDir():
	userPath = expanduser('~')
	return userPath if  platform != 'Windows' else ('%s\\AppData\\Roaming' % userPath)
