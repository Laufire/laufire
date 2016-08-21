import logging

from colorama import Fore, Style, init as colorama_init

# Delegates
Logger = logging.getLogger()

# Exports
__all__ = ['log', 'logError', 'debug']

BRED = '%s%s' % (Style.BRIGHT, Fore.RED) #pylint: disable=E1101

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
			lvl	 (int): Could be one of the following integers (1, 2, 3, 4, 5). The greater the number lesser the logs.
	"""
	Logger.setLevel(lvl * 10)

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
