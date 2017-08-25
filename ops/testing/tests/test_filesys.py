r"""Test the module, filesys.
"""
import unittest

from laufire.logger import debug
from laufire.filesys import ensureDir, removePath, setContent
from laufire.parser import parse

Config = parse('data/config.yaml')
tempDir = Config['Paths']['temp']
TestConfig = Config['Testing']

# Helpers
def buildStructure(base, Structures):
	for k, v in Structures.iteritems():
		dirPath = '%s/%s' % (base, k)
		removePath(dirPath)
		ensureDir(dirPath)

		for i in v:
			if hasattr(i, 'iteritems'):
				buildStructure(dirPath, i)

			else:
				subPath = '%s/%s' % (dirPath, i)
				setContent(subPath, subPath)

# Tests
class TestFileSys(unittest.TestCase):
	def test_collectPaths(self):
		r"""Tests the function collectPaths.
		"""
		debug('Setting up...')
		buildStructure(tempDir, TestConfig['FS'])

		from laufire.filesys import collectPaths

		print list(collectPaths('%s/base' % tempDir))
