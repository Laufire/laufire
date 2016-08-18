r"""The standard project file for the support package, laufire.
"""
#pylint: disable=W0611

from laufire.initializer import init


# Config
name = 'laufire'

from Store import Store

devMode = True

# Init
init() # #Note: This call will add the Config object to the module.
