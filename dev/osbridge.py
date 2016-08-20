r"""
OS Bridge
=========

A multi platform adapter.
"""

import platform

from os.path import expanduser

# Data
platform = platform.system()

def getDataFolder():
	userPath = expanduser('~')
	return userPath if  platform != 'Windows' else ('%s\\AppData\\Roaming' % userPath)
