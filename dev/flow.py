r"""
flow
----

A module to control the flow of the application.
"""
from time import sleep

from laufire.logger import debug

from Project import delay

defaultDelay = delay / 1.0 # Get a float value.
tickTime = defaultDelay / 10

def waitFor(func, maxWait=defaultDelay):
	r"""Waits for the given function to return a truthy or until a set time.
	"""
	waited = 0

	while not func():
		waited += tickTime

		if waited > maxWait:
			raise Exception('Maximum wait time exceded.')

		debug('Waited: %d, MaxWait: %d.' % (waited, maxWait))
		sleep(tickTime)

def forgive(func):
	try:
		func()

	except Exception as e: #pylint: disable=W0703
		return e

def rob(func):
	r"""Tries to get the result from a given function, and returns none if there were a error.
	"""
	try:
		return func()

	except: #pylint: disable=W0702
		return

def retry(func, repeat=3, delay=tickTime * 2):
	while repeat:
		result = func()

		if result is None and delay:
			sleep(delay)

		else:
			return result

		repeat -= 1
