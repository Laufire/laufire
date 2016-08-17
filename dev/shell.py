r"""A module to help with shell calls.
"""
import sys
import os

from subprocess import Popen, PIPE
from shlex import split as shlexSplit

from laufire.logger import debug

# State
split = None

# Helpers
def getNthLine(string, N):
	return string.strip().split('\n')[N]

# Exports
def run(command, **kwargs):
	r"""Starts a process, waits till the process completes and returns the return-code.

	#Tip: Use this method to live stream output from the command.
	"""
	debug(command)
	debug(kwargs)

	p = Popen(split(command), **kwargs)
	p.wait()

	return p.returncode

def call(command, **kwargs): # from gitapi.py
	r"""Starts a process, waits till the process completes and returns a dictionary with the return-code, stdout and stderr.

	#Tip: Use this method when there's a need to process stdout or stderr.
	"""
	debug(command)
	debug(kwargs)

	p = Popen(split(command), stdout=PIPE, stderr=PIPE, **kwargs)
	out, err = [x.decode("utf-8") for x in p.communicate()]

	return {'out': out, 'err': err, 'code': p.returncode}

def debugCall(command, **kwargs):
	r"""Starts a process, waits till the process completes and returns a dictionary with the return-code, stdout and stderr.

	#Tip: Use this method call scripts during development, errors would be logged to the live stderr, at the same time stdout could be buffered for processing.
	#Tip: A modified pdb like, modPdb = pdb.Pdb(stdout=sys.__stderr__), could be used to debug scripts in stderr.
	"""
	debug(command)
	debug(kwargs)

	p = Popen(split(command), stdout=PIPE, **kwargs)
	out = p.communicate()[0].decode("utf-8")

	return {'out': out, 'err': '', 'code': p.returncode}

def launch(command, **kwargs):
	r"""Launches a process and quits without waiting for its completion.
	"""
	debug(command)
	debug(kwargs)

	Popen(split(command), stdout=PIPE, stderr=PIPE, **kwargs)

class CwdSwitch:
	r"""Helps with switching the CWD.
	"""
	def __init__(self, baseDir=None):
		self.cwd = baseDir or os.getcwd()

	def switch(self, newCwd):
		os.chdir(newCwd)

	def restore(self):
		os.chdir(self.cwd)


def assertShell(ShellResult, errorLine=None):
	r"""Asserts the success of a shell command.
	"""
	debug(ShellResult)

	if ShellResult['code']:
		errorStr = ShellResult['err'] or ShellResult['out']

		if errorLine is not None:
			errorStr = getNthLine(errorStr, errorLine)

		raise Exception(errorStr)

	return ShellResult['out']

def extendEnv(**Extensions):
	Env = dict(**os.environ)
	Env.update(Extensions)

	return Env

# Init
def init():
	global split

	if 'win' not in sys.platform:
		split = shlexSplit

	else:
		from re import compile
		quoted = compile('^"(.+)"$')

		def _split(command): # #Note: This is just a crude implementaion to split windows command lines.
			Parts = []

			for item in shlexSplit(command, posix=False):
				match = quoted.match(item)

				Parts.append(match.groups(1)[0] if match else item)

			return Parts

		split = _split

init()
