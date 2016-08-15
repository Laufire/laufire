r"""
dev
---

A module to help with develpment.
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

# Pretty prints the given iterable (dictionary, list etc).
def pPrint(Iterable, indent=0):
	for key, value in pairs(Iterable):
		if hasattr(value, 'iteritems') or hasattr(value, 'next'): #pylint: disable=W1504
			print '%s%s:' % ('\t' * indent, key)
			pPrint(value, indent + 1)

		else:
			print '%s%s: %s' % ('\t' * (indent), key, value)

	print ''
