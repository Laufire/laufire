r"""
initializer
===========

	Intializes the Project and gives it the Config.

#Note: A project option ensureCWD is thought, but was skipped from being added, as the Project file itself, won't be resolced if the CWD isn't right.
"""
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
	from laufire.extensions import merge
	from laufire.yamlex import YamlEx

	configPath = Attrs.get('configPath')

	Config = YamlEx(configPath, loglevel='ERROR') if configPath else YamlEx(loglevel='ERROR')

	Data = Config.data

	if 'ConfigExtensions' in Attrs:
		Data = merge(Data, Attrs['ConfigExtensions'])

	if 'Store' in Attrs:
		Data = merge(Data, Attrs['Store'].var(''))

	Config.setData(Data)
	Config.interpolate()

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

def setSettings():
	from sys import modules

	for moduleName in ['flow', 'filesys', 'logger']:
		moduleName = 'laufire.%s' % moduleName

		if moduleName in modules:
			modules[moduleName].setup(Project)

def loadProjectSettings(setupCall):
	if Project:
		setupCall(Project)

# Init
def init():
	r"""Initializes the project.

	# #Note: The Project file has to be in the path for proper initialization.
	"""
	import Project as _Project

	global Project
	Project = _Project

	Attrs = getAttrDict(Project, 'configPath', 'ConfigExtensions', 'Store', 'LoggersToSilence')

	silenceLoggers(Attrs) # #Later: Think of silencing every other log, than that of the project or those that are excluded.

	Project.Config = collectConfigData(Attrs)

	addDefaults()

	addDevBuiltins()

	setSettings()
