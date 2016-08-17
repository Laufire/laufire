r"""
OS Bridge
=========

A multi platform adapter.
"""

import platform

from os.path import expanduser

def getDataFolder():
	userPath = expanduser('~')
	return ('%s\\AppData\\Roaming' % userPath) if platform.system() == 'Windows' else userPath
