r"""
flow
----

A module to control the flow of the application.
"""
from time import sleep

from laufire.logger import debug, log

defaultDelay = 0
tickTime = 0.1

def waitFor(func, maxWait=None, message=None):
	r"""Waits for the given function to return a truthy or until a set time.
	"""
	waited = 0
	maxWait = maxWait or defaultDelay

	if message:
		log(message)

	while True:

		ret = func()

		if ret:
			return ret

		waited += tickTime

		if waited > maxWait:
			raise Exception('Maximum wait time exceded.' if not message else 'Failed waiting for: %s' % message)

		if message:
			debug(message)

		debug('Waited: %d, MaxWait: %d.' % (waited, maxWait))
		sleep(tickTime)

def forgive(func):
	try:
		func()

	except Exception as e: #pylint: disable=W0703
		debug(e)
		return e

def rob(func):
	r"""Tries to get the result from a given function, and returns none if there were an error.
	"""
	try:
		return func()

	except: #pylint: disable=W0702
		return

def retry(func, repeat=3, delay=tickTime * 2):
	r"""
	Calls the given function till it returns a value.

	Set repeat to -1, to try untill success.
	"""
	while repeat:
		result = func()

		if result is None and delay and repeat != 1:
			sleep(delay)

		else:
			return result

		repeat -= 1

# Init
def setup(Project):
	delay = Project.delay / 1.0 # Get a float value.

	global defaultDelay, tickTime

	defaultDelay = delay
	tickTime = defaultDelay / 10

from laufire.initializer import loadProjectSettings #pylint: disable=C0413
loadProjectSettings(setup)
