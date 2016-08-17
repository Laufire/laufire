r"""
dev
---

A module to help with develpment.

#Later: Think of adding some functions, like scan, to the built-ins, so that there can be used without importing.
"""
from laufire.flow import forgive
from laufire.extensions import pairs

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

# Pretty prints the given iterable (dictionary, list etc).
def pPrint(Iterable, indent=0):
	for key, value in pairs(Iterable):
		if hasattr(value, 'iteritems') or hasattr(value, 'next'): #pylint: disable=W1504
			print '%s%s:' % ('\t' * indent, key)
			pPrint(value, indent + 1)

		else:
			print '%s%s: %s' % ('\t' * (indent), key, value)

	print ''
