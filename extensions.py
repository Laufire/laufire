r"""
extensions
==========
Functions to ease development.
"""
import sys

# Helpers
def getCallingModule():
	return sys.modules[sys._getframe().f_back.f_back.f_globals['__name__']] #pylint: disable=W0212

# Exports
def namespace(wrapper):
	r"""A decorator that allows functions to have private variables. This helps with simulating sub modules.
	"""
	returned = wrapper()

	if isinstance(returned, tuple): # we've got multiple items hence set the attributees of the module directly, instead of returning a decorated function

		CallingModule = getCallingModule()

		for item in returned:
			setattr(CallingModule, item.__name__, item)

	else: # copy the function signature from the wrapper to the decorated function.
		returned.__name__ = wrapper.__name__
		returned.__doc__ = wrapper.__doc__
		returned.__dict__.update(wrapper.__dict__)

		return returned

def flattenDict(d):
	r"""Returns a flattened list from the values of a dictionary.(from: http://stackoverflow.com/questions/13490963/how-to-flatten-a-nested-dictionary-in-python-2-7x)
	"""
	l = []

	for v in d.values():
		if isinstance(v, dict):
			for item in flattenDict(v):
				l += item
		else:
			l += v

	return l

def flattenList(inList):
	r"""Returns a flattened copy of a nested list.
	"""
	l = []

	for item in inList:
		if isinstance(item, list):
			for child in flattenList(item):
				l.append(child)

		else:
			l.append(item)

	return l

def walkDict(Obj, callback):
	for key, val in Obj.iteritems():
		if isinstance(val, dict):
			walkDict(val, callback)

		else:
			callback(val, key, Obj)
