r"""
main
====

	The entry point for Ops.
"""
import os
import re

from ec.ec import arg, settings, task
from ec.types import basics, multi

from Project import Config

# Data
Paths = Config['Paths']
testsDir = Paths['tests']
testFilePattern = '^test_(\\w+).py$'
TestNames = list(re.search(testFilePattern, i).group(1) for i in os.listdir(testsDir) if re.search(testFilePattern, i))

# Helpers
def call(*Args, **KWArgs):
	from laufire.shell import assertShell, call
	assertShell(call(*Args, **KWArgs))

# Tasks
@task(alias='c')
def cleanUp():
	r"""Cleans up residue from the project dir.
	"""
	from laufire.filesys import removePath
	removePath(Paths['temp'])

@task(alias='b')
def build(target='./dist'):
	r"""Builds a wheel under the given dir.
	"""
	call('python setup.py bdist_wheel', cwd='..')

	return 'Wheel built, under: %s' % target

@task(alias='id')
def installDev(): # #Note: The project needs the library to start. Hence this command could be used, only to replace a production version, with a development one.
	r"""Installs a development version of the library.
	"""
	call('python setup.py develop', cwd='..')

@task(alias='t')
@arg(type=multi.one_of(TestNames + ['*']), sep='\n\t')
@arg(type=basics.yn)
@arg(type=basics.yn)
def test(testName='*', isVerbose=False, debug=False):
	r"""The task under development.
	"""
	from laufire.shell import run

	cleanUp()

	if debug:
		testFile = ('%s/test_%s.py' % (Config['Paths']['tests'], testName)) if testName != '*' else ''
		assert run('nosetests -vsx --pdb %s' % testFile, shell=True) == 0, 'Testing failed.'

	else:
		assert run('python -m unittest discover -s "%s" -p test_%s.py -fc%s' % (Config['Paths']['tests'], testName, 'v' if isVerbose else ''), shell=True) == 0, 'Testing failed.'

settings(debug=Config['debug'])
