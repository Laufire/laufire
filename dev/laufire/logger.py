r"""
A module to help with logging.

The reason for a custom module is due to different preferences in the output levels and style.
"""

import logging

from colorama import Fore, Style, init as colorama_init

# Delegates
Logger = logging.getLogger('<unnamed>')

# Exports
__all__ = ['log', 'logError', 'debug']

# Data
BRED = '%s%s' % (Style.BRIGHT, Fore.RED) #pylint: disable=E1101

# State
Supressed = []

def log(message, color=None):
	r"""Facilitates colored logging.
	"""
	Logger.info('%s%s' % (getattr(Fore, color, 'WHITE'), message) if color else message)

def logError(message):
	r"""Logs an error.
	"""
	Logger.error('%s%s\n' % (BRED, message)) #pylint: disable=W1201

def dump(message):
	if Logger.level > 1:
		Supressed.append(message)

	else:
		Logger.debug(message)

def debug(message):
	if Logger.level > 10:
		Supressed.append(message) #Pending: Add a max-size setting for the Buffer.

	Logger.debug(message)

def setLevel(lvl):
	r"""Sets the level of the Logger.

		Args:
			lvl	 (int): Could be one of the following integers (1, 2, 3, 4, 5). The greater the number lesser the logs.
	"""
	Logger.setLevel((lvl * 10) or 1) # #Note: 0 silences the logger.

# Init
def setup(Project):
	Logger.name = Project.name
	setLevel(Project.logLevel)

def init():
	colorama_init(autoreset=True)

	from laufire.initializer import loadProjectSettings
	loadProjectSettings(setup)

	Logger.addHandler(logging.StreamHandler())
	Logger.setLevel(logging.INFO)

init()
