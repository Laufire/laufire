r"""
A module to help with decorating functions.
"""
import json

from laufire.utils import getMD5ForIterable

# State
Memory = {}

# Helpers
def getHash(Data):
	r"""Returns the hash of the JSON of the given Data.
	"""
	return getMD5ForIterable(getJSON(Data, sort_keys=True)) # #Note: JSON output has to be sorted by keys, for the output to be deterministic.

def getJSON(value, sort_keys=True):
	return json.dumps(value, ensure_ascii=False, sort_keys=sort_keys)

def _getMemoizeKey(function, *Args, **KWArgs):
	Data = {

		'Args': [id(arg) for arg in Args],
		'KWArgs': {k: id(v) for k, v in KWArgs.iteritems()}
	}

	return '%s.%s/%s' % (function.__module__, function.__name__, getHash(Data))

# Exports
def wrap(function, wrapper):
	r"""
	Wraps the function with the given wraper.
	"""
	# Copy the function signature.
	wrapper.__module__ = function.__module__
	wrapper.__name__ = function.__name__
	wrapper.__doc__ = function.__doc__

# Decorators
def memoize(function):
	r"""
	A decorator to help with buffering (non-persistent) the results of function calls.
	# #Note: Use memoize, only when the calls are sufficiently costly. Else, memoization itself could add to the cost.
	"""
	def wrapper(*Args, **KWArgs):

		key = _getMemoizeKey(function, *Args, **KWArgs)

		if key in Memory:
			return Memory[key]

		Ret = function(*Args, **KWArgs)

		Memory[key] = Ret

		return Ret

	wrap(function, wrapper)

	return wrapper

# Tools
def rerun(function, *Args, **KWArgs):
	r"""
	Re-runs the memoized function and re-memoizes the result.
	"""
	key = _getMemoizeKey(function, *Args, **KWArgs)

	if key in Memory:
		del Memory[key] # Clear existing data, thus force a recalculation.

	return function(*Args, **KWArgs) # #Note: This value will be memoized.
