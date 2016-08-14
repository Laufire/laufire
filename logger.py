# #ToDo: Fix colored logging.

import logging

from colorama import Fore, Style, init as colorama_init

from Project import name as projectName

# State
Logger = logging.getLogger(projectName)

# Exports
__all__ = ['log', 'logError', 'debug']

BRED = '%s%s' % (Style.BRIGHT, Fore.RED) #pylint: disable=E1101

def init():
	colorama_init(autoreset=True)

	Logger.addHandler(logging.StreamHandler())
	Logger.setLevel(logging.DEBUG)

def log(message, color=None):
	r"""Facilitates colored logging.
	"""
	Logger.info('%s%s' % (getattr(Fore, color, 'WHITE'), message) if color else message)

def logError(message):
	r"""Logs an error.
	"""
	Logger.error('%s%s\n' % (BRED, message)) #pylint: disable=W1201

debug = Logger.debug

def setLevel(lvl):
	r"""Sets the level of the Logger.

		Args:
			lvl	 (int): Could be one of the following integers (10, 20, 30, 40, 50). The greater the number lesser the logs.
	"""
	Logger.setLevel(lvl)

# Main
init()
