r"""Test the module, filesys.
"""
import re
import unittest

from laufire.logger import debug
from laufire.filesys import collectPaths, ensureCleanDir, ensureDir, removePath, setContent
from laufire.parser import parse

# Data
Config = parse('data/config.yaml')
tempDir = Config['Paths']['temp']
baseDir = '%s/base' % tempDir
TestConfig = Config['Testing']

# Helpers
def getFSDict(prefix, Structure, Buffer):
	r"""
	Returns a dictionaty of paths and pathTyeps.
	"""
	if isinstance(Structure, list):
		for item in Structure:
			getFSDict(prefix, item, Buffer)

	elif isinstance(Structure, basestring):
		Buffer['%s/%s' % (prefix, Structure) if prefix else Structure] = 1

	else:
		k = Structure.keys()[0]
		dir = '%s/%s' % (prefix, k) if prefix else k
		Buffer[dir] = 2
		getFSDict(dir, Structure[k], Buffer)

	return Buffer

def buildStructure(base, FSDict):
	for k, v in FSDict.iteritems():
		if v == 2:
			ensureDir('%s/%s' % (base, k))

	for k, v in FSDict.iteritems():
		if v == 1:
			setContent('%s/%s' % (base, k), k)

def ensureValidPathCollection(collectPathsPattern, regexValidator, invert=False):
	assert cmp(

		{Pair[0]: Pair[1] for Pair in collectPaths(baseDir, collectPathsPattern)},
		{k: v for k, v in FSDict.iteritems() if bool(re.match('^%s$' % regexValidator, k)) == (not invert)},

		) == 0, 'collectPaths failed on: %s' % collectPathsPattern

# Data
FSDict =  getFSDict('', TestConfig['FS']['base'], {})

# Tests
class TestFileSys(unittest.TestCase):
	def test_collectPaths(self):
		r"""Tests the function collectPaths.
		"""
		debug('Setting up...')
		ensureCleanDir(baseDir)
		buildStructure(baseDir, FSDict)

		debug('Testing proper collections...')
		ensureValidPathCollection('**', r'.*')
		ensureValidPathCollection('*', r'[^\/]*')
		ensureValidPathCollection('*d*', r'[^\/]*d[^\/]*')
		ensureValidPathCollection('*.txt', r'[^\/]*\.txt')
		ensureValidPathCollection('.*', r'\.[^\/]*')
		ensureValidPathCollection('*.py*', r'[^\/]*\.py[^\/]*')
		ensureValidPathCollection('**/dir1/**', r'.*\/dir1\/.*')
		ensureValidPathCollection('*ir1/**', r'[^\/]*ir1\/.*')
		ensureValidPathCollection('**/*ir1/**', r'.*\/[^\/]*ir1\/.*')

		debug('Testing empty collections...')
		ensureValidPathCollection('**/*2/**', '')
		ensureValidPathCollection('dir', '')

		debug('Testing exclusions...')
		ensureValidPathCollection('**!**', r'.*', True)
		ensureValidPathCollection('**!*.txt', r'[^\/]*\.txt', True)
		ensureValidPathCollection('*!*fi*.tx*', r'.*\/.*|[^\/]*fi[^\/]*\.tx[^\/]*', True)
