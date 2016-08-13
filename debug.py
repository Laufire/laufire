r"""
debug
-----

Calls to help with debugging scripts.
"""

import sys
import inspect

def obj2dict(obj):
	return dict((name, getattr(obj, name)) for name in dir(obj) if not name.startswith('_'))

def getCallerInfo(level=2, formatted=True):
	r"""Used to get the caller of the current function.

	Args:
		level: The *nth* level of the stack.
	"""
	stack = inspect.stack()

	if level > len(stack):
		return

	Info = inspect.getframeinfo(stack[level][0])

	if not formatted:
		return Info

	ret = ''

	for item in ['filename', 'function', 'lineno']:
		ret += '%s\t%s\n' % (item, getattr(Info, item, ''))

	ret += 'code\t%s\n' % Info.code_context[0]

	return ret

def err(string):
	r"""Logs the given string to the stderr, to help with debugging.
	"""
	sys.stderr.write('%s\n' % string)
