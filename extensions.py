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

def pairs(Iterable):
	r"""Provides a generator to iterate over key, value pairs of iterables.
	"""
	return Iterable.iteritems() if hasattr(Iterable, 'iteritems') else enumerate(Iterable)

def values(Iterable):
	r"""Provides a generator to iterate over key, value pairs of iterables.
	"""
	return Iterable.values() if hasattr(Iterable, 'values') else Iterable

def isIterable(value):
	return hasattr(value, 'iteritems') or hasattr(value, 'next')

def flatten(Iterable):
	r"""Collects all the values from the given iterable.

	#From: http://stackoverflow.com/questions/13490963/how-to-flatten-a-nested-dictionary-in-python-2-7x
	"""
	l = []

	for v in values(Iterable):
		if isIterable(v):
			for item in flatten(v):
				l += item
		else:
			l += v

	return l

def walk(Iterable, Route=None):
	if Route is None:
		Route = [None]

	for key, val in pairs(Iterable):
		Route[-1 if Route else 0] = key

		if isIterable(val):
			for Route, val in walk(val, [key]):
				yield [key] + Route, val

		else:
			yield Route, val

def resolveKey(keyParts, Dict, splitter='.'):
	r"""Resolves a nested key from a dict.

	Args:
		keyParts (str / list): The key to resolve.
		Dict (dict): The dict to look up.
		splitter (str): Defaults to '.'.
	"""
	if hasattr(keyParts, 'split'): # Convert the string to a list.
		keyParts = keyParts.split(splitter)

	if not keyParts:
		return Dict

	Resolved = Dict

	for item in keyParts:
		Resolved = Resolved[item]

	return Resolved

class Lazy:
	r"""A class to implement lazy initialization. The class passed during the initialization will be initialized on first access.
	"""
	def __init__(self, Underlying, *Args, **KWArgs):
		self._data = Underlying, Args, KWArgs
		self._obj = None

	def __getattr__(self, name):
		if self._obj:
			return getattr(self._obj, name)

		Underlying, Args, KWArgs = self._data
		self._obj = Underlying(*Args, **KWArgs) #pylint: disable=W0201
		delattr(self, '_data')

		return getattr(self, name)
