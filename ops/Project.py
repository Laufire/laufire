r"""The standard project file for the support package, laufire.
"""
from laufire.initializer import init, stealCWD
from Store import Store #pylint: disable=W0611

stealCWD(__file__)

# Config
name = 'laufire'

configPath = 'data/config.yaml'

devMode = True

logLevel = Store['logLevel']

# Init
init() # #Note: This call will add the Config object to the module.
