r"""
main
====

	The entry point for Ops.
"""
import os
import re

from ec.ec import arg, settings, task
from ec.types import basics, multi
from laufire.filesys import removePath

from Project import Config

# Data
Paths = Config['Paths']
testsDir = Paths['tests']
testFilePattern = '^test_(\\w+).py$'
TestNames = list(re.search(testFilePattern, i).group(1) for i in os.listdir(testsDir) if re.search(testFilePattern, i))

@task(alias='c')
def cleanUp():
	r"""Cleans up residue from the project dir.
	"""
	removePath(Paths['temp'])

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
