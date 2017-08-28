r"""Test the module, filesys.

#Pending: Test other functions.
"""
import re
import unittest

from laufire.logger import debug
from laufire.filesys import abspath, collectPaths, copy, ensureCleanDir, ensureDir, getAncestor, isDescendant, linkTree, removePath, requireAncestor, setContent, stdPath
from laufire.flow import forgive
from laufire.parser import parse

# Data
Config = parse('data/config.yaml')
tempDir = abspath(Config['Paths']['temp'])
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

def getStructureDict(base, pattern='**', excludeDirs=False):
	return {k: v for k, v in collectPaths(base, pattern) if not excludeDirs or v == 1}

def buildStructure(base, FSDict):
	for k, v in FSDict.iteritems():
		if v == 2:
			ensureDir('%s/%s' % (base, k))

	for k, v in FSDict.iteritems():
		if v == 1:
			setContent('%s/%s' % (base, k), k)

def rebuildStructures():
	debug('Building Structures...')
	ensureCleanDir(baseDir)
	buildStructure(baseDir, FSDict)

def testScenarios(tester, *Scenarios):
	for Scenario in Scenarios:
		tester(*Scenario)

# Data
FSDict = getFSDict('', TestConfig['FS']['base'], {})

# Tests
class TestFileSys(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		from laufire import filesys
		filesys.fsRoot = filesys.dirname(tempDir)

	def tearDown(self):
		removePath(tempDir)

	def test_isDescendant(self):
		ensureDir(baseDir)

		assert isDescendant(baseDir, tempDir)
		assert not isDescendant(tempDir, baseDir)

	def test_requireAncestor(self):
		assert not requireAncestor(baseDir, tempDir)
		assert forgive(lambda: requireAncestor(tempDir, baseDir))

	def test_getAncestor(self):
		ensureDir(baseDir)

		Lineage = stdPath(abspath(baseDir)).split('/')
		l = len(Lineage)
		Reversed = Lineage[:]
		Reversed.reverse() # Names are checked from last to first.

		for name in Lineage:
			assert getAncestor(baseDir, name) == '/'.join(Lineage[:l - Reversed.index(name)]), 'getAncestor failed for the name "%s"' % name

		assert not getAncestor(baseDir, '/'), 'getAncestor returned a non-empty value for a non-existent name.'

	def test_collectPaths(self):
		r"""Tests the function collectPaths.
		"""
		rebuildStructures()

		def ensureValidPathCollection(collectPathsPattern, regexValidator, invert=False):
			assert cmp(

				{Pair[0]: Pair[1] for Pair in collectPaths(baseDir, collectPathsPattern)},
				{k: v for k, v in FSDict.iteritems() if bool(re.match('^%s$' % regexValidator, k)) == (not invert)},

				) == 0, 'collectPaths failed on: %s' % collectPathsPattern

		debug('Testing proper collections...')
		testScenarios(ensureValidPathCollection,

			('**', r'.*'),
			('*', r'[^\/]*'),
			('*d*', r'[^\/]*d[^\/]*'),
			('*.txt', r'[^\/]*\.txt'),
			('**.txt', r'.*\.txt'),
			('.*', r'\.[^\/]*'),
			('*.py*', r'[^\/]*\.py[^\/]*'),
			('**/dir1/**', r'.*\/dir1\/.*'),
			('*ir1/**', r'[^\/]*ir1\/.*'),
			('**/*ir1/**', r'.*\/[^\/]*ir1\/.*'),
		)

		debug('Testing empty collections...')
		testScenarios(ensureValidPathCollection,

			('**/*2/**', ''),
			('dir', ''),
		)

		debug('Testing exclusions...')
		testScenarios(ensureValidPathCollection,

			('**!**', r'.*', True),
			('**!*.txt', r'[^\/]*\.txt', True),
			('*!*fi*.tx*', r'.*\/.*|[^\/]*fi[^\/]*\.tx[^\/]*', True),
		)

	def test_copy(self): # #Pending: Test all the argument combinations.
		rebuildStructures()

		target = '%s/base1' % tempDir
		copy(baseDir, target)

		assert cmp(getStructureDict(baseDir), getStructureDict(target)) == 0, 'The structures do not match.'

	def test_linkTree(self): # #Pending: Test all the argument combinations.
		rebuildStructures()

		debug('Testing with default arguments...')
		target = '%s/base1' % tempDir
		linkTree(baseDir, target)
		assert cmp(getStructureDict(baseDir), getStructureDict(target)) == 0, 'The structures do not match.'
		removePath(target)

		debug('Testing patterns...')

		def testPattern(pattern, excludeDirs=False):
			linkTree(baseDir, target, pattern)
			assert cmp(getStructureDict(baseDir, pattern), getStructureDict(target, excludeDirs=excludeDirs)) == 0, 'The structures do not match.' # #Note: pattern isn't fed into getStructureDict(target) to avoid mirror bias (those calls that go wrong on both sides, thus equate and pass).

		testPattern('**!**.txt')
		testPattern('**.txt', True)
