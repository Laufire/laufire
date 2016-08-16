r"""
initializer
===========

	Intializes the Project and gives it the Config.

"""
from laufire.yamlex import YamlEx

# State
Project = None

# Helpers
def getAttrDict(Obj, *Attrs):
	Ret = {}

	for attr in Attrs:
		if hasattr(Obj, attr):
			Ret[attr] = getattr(Obj, attr)

	return Ret

def collectConfigData(Attrs):
	r"""Collects the config from various sources and builds the Config.
	"""
	Config = YamlEx(Attrs['configPath'], loglevel='ERROR')

	if 'ConfigExtensions' in Attrs:
		Config.update(Attrs['ConfigExtensions'])

	Config.interpolate()

	if 'Store' in Attrs:
		Config.update(Attrs['Store'].var(''))

	return Config

def silenceLoggers(Attrs):
	# #Later: Fix: Logging seems not to be silenced.

	LoggerNames = Attrs.get('LoggersToSilence')

	if not LoggerNames:
		return

	import logging

	for name in LoggerNames:
		logging.getLogger(name).setLevel('ERROR') # only log really bad events

def addDefaults():
	# Load the project with default values for the essential attributes.
	from laufire.setup import Defaults

	for key, value in Defaults.iteritems():
		if not hasattr(Project, key):
			setattr(Project, key, value)

def addDevBuiltins():
	if not Project.devMode:
		return

	from laufire import dev
	import __builtin__

	for attr in ['pPrint', 'peek', 'details']:
		setattr(__builtin__, attr, getattr(dev, attr))

# Main
def init():
	import Project as _Project

	global Project
	Project = _Project

	Attrs = getAttrDict(Project, 'configPath', 'ConfigExtensions', 'Store', 'LoggersToSilence')

	silenceLoggers(Attrs) # #Later: Think of silencing every other log, than that of the project or those that are excluded.

	Project.Config = collectConfigData(Attrs)

	addDefaults()

	addDevBuiltins()
