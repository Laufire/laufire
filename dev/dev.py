r"""
dev
---

A module to help with develpment.

#ToDo: Ensure that unicode's are handled well by get pretty.
#Later: Think of adding some functions, like scan, to the built-ins, so that there can be used without importing.
"""
from laufire.flow import forgive
from laufire.extensions import pairs, isIterable

# Workers
def _getPretty(Iterable, indent):
	ret = ''

	for key, value in pairs(Iterable):
		if isIterable(value): #pylint: disable=W1504
			ret += u'%s%s:\n%s\n' % (u'\t' * indent, unicode(key), _getPretty(value, indent + 1))

		else:
			ret += u'{0}{1}: {2}\n'.format(u'\t' * indent, unicode(key), unicode(value))

	return ret.encode('utf-8')

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

def pause(message='Paused! Press return to continue ...'):
	raw_input(message)

def peek(val):
	print val
	return val

def details(Obj):
	for attr in [attr for attr in dir(Obj) if attr[0] != '_']:
		print '%s: %s' % (attr, getattr(Obj, attr))

	return Obj

# Makes pretty the given iterable (dictionary, list etc).
def getPretty(Iterable):
	ret = ''

	if not isIterable(Iterable):
		return str(Iterable)

	return _getPretty(Iterable, 0).replace('\n\n\n', '\n\n')

# Pretty prints the given iterable.
def pPrint(obj):
	print getPretty(obj) if isIterable(obj) else obj
	return obj

# Plots the given list of numbers.
def plot(Values):
	import matplotlib.pyplot as plt

	plt.plot(Values)
	plt.grid(True)

	plt.show()
