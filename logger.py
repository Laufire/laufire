# #ToDo: Fix colored logging.

import logging

from colorama import Fore, Style

from Project import name as projectName

# State
Logger = logging.getLogger(projectName)

# Exports
__all__ = ['log', 'logError', 'debug']

# #Note: This is an workaround for https://github.com/tartley/colorama/issues/57
RESET = '%s%s' % (Style.DIM, Fore.RESET) #pylint: disable=E1101
RED = '%s%s' % (Style.BRIGHT, Fore.RED) #pylint: disable=E1101

def init():
	Logger.addHandler(logging.StreamHandler())
	Logger.setLevel(logging.DEBUG)

	from colorama import init as colorama_init
	colorama_init()

def log(message, color=None):
	r"""Facilitates colored logging.
	"""
	Logger.info('%s%s%s' % (getattr(Fore, color, 'WHITE'), message, RESET) if color else message)
	# print '%s%s%s' % (getattr(Fore, color, 'WHITE'), message, RESET) if color else message # #Fix: Log isn't supporting colored logging.

def logError(message):
	r"""Logs an error.
	"""
	Logger.error('%s%s%s\n' % (RED, message, RESET)) #pylint: disable=W1201

debug = Logger.debug

def setLevel(lvl):
	r"""Sets the level of the Logger.

		Args:
			lvl	 (int): Could be one of the following integers (10, 20, 30, 40, 50). The greater the number lesser the logs.
	"""
	Logger.setLevel(lvl)

# Main
init()
