r"""
initializer
===========

	Intializes the Project and gives it the Config.

"""
from laufire.yamlex import YamlEx

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

# Main
def init():
	import Project

	Attrs = getAttrDict(Project, 'configPath', 'ConfigExtensions', 'Store', 'LoggersToSilence')

	silenceLoggers(Attrs)
	Project.Config = collectConfigData(Attrs)
