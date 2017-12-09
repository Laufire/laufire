r"""
initializer
===========

	Intializes the Project and gives it the Config.
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

def setCWD(cwd):
	if cwd:
		from os import chdir

		chdir(cwd)

def addPaths(Paths):
	r"""Adds additional paths for module lookup.
	"""
	if Paths:
		from sys import path
		from os.path import abspath

		Paths.reverse()

		for item in Paths:
			path.insert(0, abspath(item))

def collectConfigData(Attrs):
	r"""Collects the config from various sources and builds the Config.
	"""
	from laufire.yamlex import YamlEx

	configPath = Attrs.get('configPath')

	Config = YamlEx(configPath, loglevel='ERROR') if configPath else YamlEx(loglevel='ERROR')

	if 'ConfigExtensions' in Attrs:
		Config.extend(Attrs['ConfigExtensions'])

	if 'fsRoot' in Attrs:
		from os.path import abspath
		Config['fsRoot'] = abspath(Attrs['fsRoot'])

	if 'Store' in Attrs:
		Store = Attrs['Store']
		Config.extend(Store if isinstance(Store, dict) else Store.var('')) # Note: A store could either be a dict or an ecstore.

	Config.interpolate()

	return Config

def silenceLoggers(LoggerNames):
	# #Later: Fix: Logging seems not to be silenced.

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

	for attr in [attr for attr in dir(dev) if attr[0] != 0]: # Add all the attributes of the module, dev to built-ins.
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

	Attrs = getAttrDict(Project, 'cwd', 'Paths', 'configPath', 'fsRoot', 'ConfigExtensions', 'Store', 'LoggersToSilence')

	setCWD(Attrs.get('cwd'))

	addPaths(Attrs.get('Paths'))

	silenceLoggers(Attrs.get('LoggersToSilence')) # #Later: Think of silencing every other log, than that of the project or those that are excluded.

	Project.Config = Config = collectConfigData(Attrs)

	addDefaults()

	addDevBuiltins()

	setSettings()

	return Config

def stealCWD(scriptPath):
	from os.path import dirname

	setCWD(dirname(scriptPath))
