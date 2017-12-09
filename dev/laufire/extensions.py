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

def isIterable(obj):
	return hasattr(obj, 'iteritems') or hasattr(obj, '__iter__')

def pairs(Iterable):
	r"""Provides a generator to iterate over key, value pairs of iterables.
	"""
	return Iterable.iteritems() if hasattr(Iterable, 'iteritems') else enumerate(Iterable)

def values(Iterable):
	r"""Provides a generator to iterate over key, value pairs of iterables.
	"""
	return Iterable.values() if hasattr(Iterable, 'values') else Iterable

def flatten(Iterable, recurse=False):
	r"""Collects all the values from the given iterable.

	#From: http://stackoverflow.com/questions/13490963/how-to-flatten-a-nested-dictionary-in-python-2-7x
	"""
	l = []

	for v in values(Iterable):
		if isIterable(v):
			for item in (flatten(v) if recurse else values(v)):
				l.append(item)
		else:
			l.append(v)

	return l

def combine(*Dicts):
	r"""
	Combines values from multiple dictionaries and returns a new dictionary. The values are overwritten by every following dictionary.
	"""
	Ret = {}

	for Dict in Dicts:
		Ret.update(Dict)

	return Ret

def merge(*Dicts):
	r"""
	Recursively merges the passed dictionaries.
	"""
	Ret = {}

	for Dict in Dicts:
		for key, value in Dict.iteritems():
			if key in Ret:
				tgtValue = Ret[key]

				if hasattr(tgtValue, 'iteritems') and hasattr(value, 'iteritems'):
					value = merge(tgtValue, value)

				Ret[key] = value

			else:
				Ret[key] = value

	return Ret

def select(Dict, Keys):
	r"""
	Returns a sub-dictionary of the given Dict with the given keys.
	"""
	return {k: Dict[k] for k in Keys}

def unpack(Dict, *Keys):
	r"""
	Unpacks the given keys of the given dictionary and assign them to the given variables.

	#Ex: a, b, c = unpack(Dict, 'a', 'b', 'c')
	"""
	return tuple(Dict[k] for k in Keys)

def walk(Iterable, RouteParts=None):
	if RouteParts is None:
		RouteParts = [None]

	for key, val in pairs(Iterable):
		RouteParts[-1 if RouteParts else 0] = key

		if isIterable(val):
			for val, RouteParts, Iterable in walk(val, [key]):
				yield val, [key] + RouteParts, Iterable

		else:
			yield val, RouteParts, Iterable

def unnest(Dict, separator='/', Target=None):
	r"""Gets a routed dictionary from a nested one.
	"""
	if Target is None:
		Target = {}

	for val, RouteParts, dummy in walk(Dict):
		Target[separator.join(RouteParts)] = val

	return Target

def resolveRoute(Dict, route, separator='/'):
	r"""Resolves a route from a nested dict.

	Args:
		Dict (dict): The dict to look up for the route.
		route (str / list): The route to resolve.
		separator (str): Defaults to '/'.
	"""
	if not route:
		return Dict

	KeyParts = route.split(separator) if hasattr(route, 'split') else route

	Resolved = Dict

	for item in KeyParts:
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
