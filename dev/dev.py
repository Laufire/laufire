r"""
dev
---

A module to help with develpment.

#Later: Think of adding some functions, like scan, to the built-ins, so that there can be used without importing.
"""
from laufire.flow import forgive
from laufire.extensions import pairs, isIterable

def interactive(func, message):
	r"""Helps with re-running tasks till there were no errors.
	"""
	while True:
		e = forgive(func)

		if not e:
			return

		print e
		if message:
			print message

		if raw_input('Fix and continue ... (Y/n):').lower() == 'n':
			return e

def pause(message='Paused! Press return t ocontinue ...'):
	raw_input(message)

def peek(val):
	print val
	return val

def details(Obj):
	for attr in [attr for attr in dir(Obj) if attr[0] != '_']:
		print '%s: %s' % (attr, getattr(Obj, attr))

	return Obj

# Makes pretty the given iterable (dictionary, list etc).
def getPretty(Iterable, indent=0):
	ret = ''

	for key, value in pairs(Iterable):
		if isIterable(value): #pylint: disable=W1504
			ret += '%s%s:\n%s\n' % ('\t' * indent, key, getPretty(value, indent + 1))

		else:
			ret += '%s%s: %s\n' % ('\t' * indent, key, value)

	return ret

# Pretty prints the given iterable.
def pPrint(obj):
	print getPretty(obj, 0) if isIterable(obj) else obj
	return obj
