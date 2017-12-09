r"""The standard project file for the support package, laufire.
"""
from laufire.initializer import init, stealCWD

stealCWD(__file__)

from Store import Store

# Config
name = 'laufire'

configPath = 'data/config.yaml'

devMode = True

logLevel = Store['logLevel'] #pylint: disable=unsubscriptable-object

# Init
stealCWD(__file__)
fsRoot = '../../../_work/%s' % name
init() # #Note: This call will add the Config object to the module.
