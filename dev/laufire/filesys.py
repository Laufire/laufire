r"""
FileSys
=======

	A module to help with files system operations.

Notes
-----

	* Path removals generally require an ancestor to be specified, so to avoid accidental deletes.
	* Many calls remove the target by default; these might not work outside the fsRoot; use removePath with requiredAncestor to achieve the same effect.
	* The module shutill isn't used as, some of its operations could be dangerous. Ex: shutil.rmtree will remove the files with-in dir junctions instead of merely removing the junction.
	* To avoid conflicts while writing outside the fsRoot, remove the target first.
	* Soft links (symlinks) are the default as they are more robust (they work even after the source is replaced).

Caution
-------

	* Debugging absolute paths could be a security risk. Hence set the appropriate logLevel.

Pending
-------

	* Check: Could links be removed, even outside the fsRoot?
	* The module doesn't handle unicode file-names. So does the package zipfile of Python2. It depends upon the type of the input path strings. ie: To call collectPaths on a dir with an unicode file name, the source dir should also be in unicode.
	* Support file encodings.
	* Add a function to copy file attributes, etc.
	* Add an isOk call to verify the correctness of the files (to avoid unresolved links etc).
	* Check: Use absPaths for robustness of the calls.
"""

import os
from os import mkdir, makedirs, unlink, rmdir
from os.path import abspath, basename, commonprefix, dirname, exists, isdir, isfile, join as pathJoin, normpath, split as pathSplit, splitext
import re

from laufire.flow import forgive
from laufire.logger import debug
from laufire.utils import getRandomString, getTimeString
from laufire.helpers.filesys import link, symlink, rmlink, isLinkedDir

# State
fsRoot = '.' # Risky filesystem operations such as removePath are limited to fsRoot.
sep = os.sep

# Data
Ext2Opener = {'zip': ('zipfile', 'ZipFile'), 'gz': 'gzip'} # #Pending: Instead of having module, object pairs import objects (for that write a support module. ie: import_obj('zipfile.ZipFile')

# Helpers
def globToRe(pattern):
	ret = r'^'
	pattern += '|'

	i = 0

	while i < len(pattern) - 1:
		c = pattern[i]

		if c != '*':
			ret += re.escape(c)

		else:
			if pattern[i + 1] != '*':
				ret += r'[^\/]*'

			else:
				ret += r'.*'
				i += 1

		i += 1

	ret += r'$'

	return ret

makeMissingDir = lambda path: exists(path) or makeDir(path)

def rmtree(tgtPath):
	r"""Removes a dir tree. It can unlink junctions (even as sub-dirs), without removing the descendant files.
	"""
	absPath = abspath(tgtPath)

	for root, Dirs, Files in os.walk(absPath):
		for file in Files:
			unlink(pathJoin(root, file))

		for dir in Dirs:
			dir = pathJoin(root, dir)

			if isLinkedDir(dir):
				rmlink(dir)

			else:
				rmtree(dir)

	rmdir(tgtPath)

def _makeLink(srcPath, tgtPath, pathType, hardLink):
	debug('link: %s => %s' % (srcPath, tgtPath))

	(link if hardLink and pathType == 1 else symlink)(abspath(srcPath), tgtPath) # #Note: Dirs can't be hard-linked.

def _removePath(tgtPath): # #Pending: Check if the call could be made more efficient.
	if not exists(tgtPath):
		return 1

	if isfile(tgtPath):
		unlink(tgtPath)

	elif isLinkedDir(tgtPath):
		rmlink(tgtPath)

	elif isdir(tgtPath):
		rmtree(tgtPath)

	else:
		return 1 # error

def _getOpener(ext):
	opener = Ext2Opener.get(ext)

	if opener:
		from importlib import import_module

		# #Pending: In the case of opening a ZipFile, if a filename within the archive isn't provided, use the first file.

		if hasattr(opener, 'upper'): # Only a module name is available. #Pending: Implement proper string validation.
			return import_module(opener).open

		return lambda filePath: getattr(import_module(opener[0]), opener[1])(filePath).open

	else:
		return lambda filePath: open(filePath, 'rb')

def doNoting(firstArg, *dummy, **dummy1):
	return firstArg

# Exports
## Path functions
stdPath = (lambda path: path.replace('\\', '/')) if sep != '/' else doNoting # Standardizes the given path.

def pair(src, tgt, postFix):
	r"""Returns a pair of the given post-fix affixed source and target paths.
	"""
	return joinPaths(src, postFix), joinPaths(tgt, postFix)

def joinPaths(*Paths):
	r"""
	Joins the given Paths.
	"""
	ret = '/'.join(Paths)

	return ret if Paths[0] else ret[1:]

def resolve(basePath, relation):
	r"""Resolves a relative path of the given basePath.

	Args:
		basePath (path): The path of the base.
		relation (str): The relation. Ex: '..', '../ops' etc.
	"""
	return abspath(pathJoin(basePath, relation))

def getFreeFilePath(parentDir, length=8):
	if exists(parentDir):
		while True:
			freePath = joinPaths(parentDir, getRandomString(length))

			if not exists(freePath):
				return freePath

def getPathType(path):
	r"""#Note: The path-types are:
		0: missing
		1: file
		2: dir
		3: linked dir
	"""
	ret = 3

	for func in [isLinkedDir, isdir, isfile]:
		if func(path):
			break

		ret -= 1

	return ret

def isLocked(filePath, tempPath=None): # #Pending: Check, whether there is a proper and robust way to check the lock status, instead of renaming the path.
	r"""Checks whether the given path is locked.
	"""
	if not exists(filePath):
		return

	if not tempPath:
		while True:
			tempPath = '%s.%s' % (filePath, getRandomString())

			if not exists(tempPath):
				break

	if forgive(lambda: rename(filePath, tempPath)):
		return True

	rename(tempPath, filePath)

	return False

def isContainer(path):
	return isdir(path) or isLinkedDir(path)

def isDescendant(probableDescendant, requiredAncestor):
	r"""Checks whether the given path is a descendant of another.

	Args:
		probableDescendant (str): The absolute path of the probable descendant.
		requiredAncestor (str): The absolute path of the required ancestor.
	"""
	requiredAncestor = abspath(requiredAncestor)

	return commonprefix([abspath(probableDescendant), requiredAncestor]) == requiredAncestor

def requireAncestor(path, requiredAncestor=None):
	r"""Ensures that the given path is a decendant of the required ancestor.
	"""
	ancestor = requiredAncestor or fsRoot

	if not isDescendant(path, ancestor):
		raise Exception('"%s" is not a descendant of "%s"' % (path, ancestor))

def getAncestor(path, ancestorName):
	r"""
	Returns the first ancestor of the given path, which has the given name.
	"""
	Lineage = abspath(path).split(sep)
	l = len(Lineage)

	while l:
		l -= 1

		if Lineage[l] != ancestorName:
			continue

		return joinPaths(*Lineage[:l + 1])

def collectPaths(base='.', pattern='**', regex=False, followlinks=True):
	r"""Returns two lists containing dirs and files of the given base dir.

	Args:
		base (str): The path to scan for.
		pattern:
			(glob): A '|' separated list of globs. Includes and excludes are separated by a '!'. Defaults to all ('**').
			(regex): A '|' separated list of regex. Includes and excludes are separated by a '$$$'. Defaults to all ('.*').
		regex (bool, False): When set to True, Includes and Excludes are parsed as regular expressions, instead of as globs.

	Glob guide:
		** : anything  (including empty strings)
		*  : anything but a slash (including empty strings)
		other characters : as is

	#From: http://stackoverflow.com/questions/5141437/filtering-os-walk-dirs-and-files
	#Note: The globs are not regular globs. But a simplified versions.
	#Note: Exclusions override inclusions.
	"""
	if regex:
		Split = pattern.split('$$$')
		includes = Split[0] or r'.*'
		excludes = Split[1] if len(Split) > 1 else None

	else:
		# transform globs to regular expressions
		Split = pattern.split('!')
		includes = r'|'.join([globToRe(x) for x in Split[0].split('|')]) if Split else r'.*'
		excludes = r'|'.join([globToRe(x) for x in Split[1].split('|')]) if len(Split) > 1 else None

	baseLen = len(base)
	match = re.match

	for root, Dirs, Files in os.walk(base, followlinks=followlinks):

		prefix = stdPath(root[baseLen+1:])

		Joined = {d: joinPaths(prefix, d) for d in Dirs}

		if excludes:
			Dirs[:] = [d for d, j in Joined.iteritems() if not match(excludes, j)] # Exclude dirs from recursion.

		for d, j in [(d1, j1) for d1, j1 in Joined.iteritems() if d1 in Dirs and match(includes, j1)]: # Yield resulting dirs.
			yield j, 2 if isdir(joinPaths(root, d)) else 3 # Check whether the path is a dir or a link.

		Files = [joinPaths(prefix, f) for f in Files]

		for file in [f for f in Files if not (excludes and match(excludes, f)) and match(includes, f)]:
			yield file, 1

def glob(base='.', pattern='**', pathType=None):
	r"""Yields the paths under the given dir matching the given glob pattern.
	"""
	jp = joinPaths

	if pathType is None:
		for path, dummy in collectPaths(base, pattern):
			yield jp(base, path)

	else:
		for path, _pathType in collectPaths(base, pattern):
			if _pathType == pathType:
				yield jp(base, path)

def getPathPairs(source, target, pattern='**', regex=False):
	r"""Iterates over the given patterns and yields a tuple with source and destination paths.
	"""
	for path, dummy in collectPaths(source, pattern, regex):
		yield pair(source, target, path)

## File manipulation functions
def removePath(tgtPath, requiredAncestor=None, forced=False):
	r"""Removes any given file / dir / junction.

	Args:
		tgtPath (path): The path to remove.
		requiredAncestor (path): The target will only be removed if it's a descendant of this dir. Defaults to the global attr fsRoot.
		forced (bool): When set to true, an ancestor won't be required.
	"""
	if not forced:
		requireAncestor(tgtPath, requiredAncestor)

	debug('remove: %s' % tgtPath)
	return _removePath(tgtPath)

def makeDir(path):
	debug('making: %s' % path)
	mkdir(path)

def makeLink(srcPath, tgtPath, autoClean=True, hardLink=False):
	r"""Links the given paths.
	"""
	if autoClean:
		removePath(tgtPath)

	ensureParent(tgtPath)

	_makeLink(srcPath, tgtPath, getPathType(srcPath), hardLink)

def rename(srcPath, tgtPath, autoClean=True):
	r"""Renames any given file / dir / junction.
	"""
	if autoClean:
		removePath(tgtPath)

	debug('rename: %s => %s' % (srcPath, tgtPath))

	os.rename(srcPath, tgtPath)

def copy(srcPath, tgtPath, pattern='**', regex=False, autoClean=True):
	r"""Copies one path to another.
	"""
	debug('copy: %s => %s' % (srcPath, tgtPath))

	if autoClean:
		removePath(tgtPath) # #Note: This also ensures that the target is under fsRoot.

	pathType = getPathType(srcPath)

	if not pathType:
		ensureParent(tgtPath)

	if pathType == 1:
		copyContent(srcPath, tgtPath)

	else:
		dirMaker = makeDir if autoClean else makeMissingDir
		copier = lambda src, tgt: copyContent(src, tgt, autoClean=False) if autoClean or not exists(tgtPath) else copyContent # File safety isn't a concern inside a missing dir.

		makeMissingDir(tgtPath)

		for Path in collectPaths(srcPath, pattern, regex):
			if Path[1] != 1:
				dirMaker(joinPaths(tgtPath, Path[0]))

			else:
				copier(*pair(srcPath, tgtPath, Path[0]))

def linkTree(srcPath, tgtPath, pattern='**', regex=False, autoClean=True, hardLink=False):
	r"""Re-creates the structure of the source at the target by creating dirs and linking files.
	"""
	_srcPath = abspath(srcPath) # Link sources should be abs-paths.
	dirMaker = makeDir if autoClean else makeMissingDir
	linkWorker = link if hardLink else symlink # Hard links aren't the default, as they can't work across drives.
	linker = linkWorker if autoClean or not exists(tgtPath) else lambda srcPath, tgtPath: (removePath(tgtPath), linkWorker(srcPath, tgtPath)) # File safety isn't a concern inside a missing dir.
	parentMaker = ensureParent if pattern != '**' and not regex else doNoting

	(ensureCleanDir if autoClean else ensureDir)(tgtPath)

	for Path in collectPaths(srcPath, pattern, regex):
		if Path[1] != 1:
			dirMaker(joinPaths(tgtPath, Path[0]))

		else:
			path = Path[0]
			_tgtPath = joinPaths(tgtPath, path)
			debug('link: %s => %s' % (joinPaths(srcPath, path), _tgtPath))
			parentMaker(_tgtPath)
			linker(joinPaths(_srcPath, path), _tgtPath)

def ensureParent(childPath):
	r"""Ensures the parent dir of the given childPathexists.

		This function is provided to ease the use of other file copying tasks.

		#Note: makedirs isn't used, as it doesn't report properly on occupied names.
	"""
	parentPath = dirname(normpath(childPath))
	Paths = []

	while parentPath and not isContainer(parentPath):
		assert not exists(parentPath), 'Parent path is occupied: %s'% parentPath # The path is occupied by a file / link.
		Paths.insert(0, parentPath)
		parentPath = dirname(parentPath)

	for path in Paths:
		makeDir(path)

def ensureDir(dir):
	r"""Ensures that the given dir is available.
	"""
	if not exists(dir):
		ensureParent(dir)
		makeDir(dir)

def ensureCleanDir(dir, requiredAncestor=None):
	r"""Ensures that the given dir is clean and available.
	"""
	removePath(dir, requiredAncestor)
	makedirs(dir)

## Content Functions
def getLines(filePath, start=-1, end=-1, ext=None, Args=None):
	r"""Yields lines from various file formats like zip, gzip etc.
	"""
	if not ext:
		ext = splitext(filePath)[1]

	n = 0

	if end < 0:
		end = float('inf')

	else:
		end += 2

	opener = _getOpener(ext.lower()[1:])(filePath)

	for line in opener if not Args else opener(*Args):
		n += 1

		if n > start:
			if n < end:
				yield line

			else:
				break

def getContent(filePath):
	r"""Reads a file and returns its content.
	"""
	return open(filePath, 'rb').read()

def iterateContent(filePath, width=4096):
	r"""Reads the given file as small chunks. This could be used to read large files without buffer overruns.
	"""
	with open(filePath, 'rb') as file:
		for chunk in iter(lambda: file.read(width), b''):
			yield chunk

def setContent(filePath, content, autoClean=True):
	r"""Fills the given file with the given content.
	"""
	if (removePath(filePath) == 1 if autoClean else True): # Ensure parent only if the path is not removed.
		ensureParent(filePath)

	open(filePath, 'wb').write(content)

def appendContent(filePath, content):
	r"""Appends the given file with the given content.
	"""
	if not exists(filePath):
		return setContent(filePath, content)

	open(filePath, 'ab').write(content)

def copyContent(srcPath, tgtPath, autoClean=True):
	r"""
	Copies the content of one file to another.

	# #Note: Unlike shutil.copy attributes aren't copied.
	"""
	debug('copy: %s => %s' % (srcPath, tgtPath))

	if (removePath(tgtPath) == 1 if autoClean else True): # Ensure parent only if the path is not removed.
		ensureParent(tgtPath)

	with open(tgtPath, 'wb') as tgt:
		for chunk in iterateContent(srcPath):
			tgt.write(chunk)

def compress(srcPath, tgtPath): # #Note: shutil.make_archive isn't used, due to its forcing of the zip extension and due to the need for maintaing a compression standard.
	if not exists(srcPath):
		raise('No such path: %s' % srcPath)

	ensureParent(tgtPath)

	from zipfile import ZipFile, ZIP_DEFLATED

	ZipFileObj = ZipFile(tgtPath, 'w', ZIP_DEFLATED)

	cwd = os.getcwd() # The CWD circus is to reduce the relpath calls.

	if isContainer(srcPath):
		os.chdir(srcPath)

		for root, dummy1, Files in os.walk('.', followlinks=True):
			for file in Files:
				ZipFileObj.write(pathJoin(root, file))

	else:
		dir, name = pathSplit(srcPath)
		os.chdir(dir)

		ZipFileObj.write(name)

	os.chdir(cwd)

	ZipFileObj.close()

def extract(srcPath, tgtPath): # #Note: The tagertPath points to the extraction root. Hence, it should be a dir.
	from zipfile import ZipFile

	with ZipFile(srcPath, 'r') as Z:
		Z.extractall(tgtPath)

def backup(srcPath, backupBase=None, addTimeString=True, keepOriginal=False): # #Pending: Change the name of the call to preserve or safeguard. As the current name could be misleading.
	r"""Backs up the given path to a temporary location, so that the returned path could be later used to restore it to the original location.

	When backupBase isn't given the path is renamed, not moved.
	# #Note: This call along with restore, could preserve links.
	"""
	if not backupBase:
		backupBase = dirname(abspath(srcPath))

	tgtPath = '%s%s.bak' % (pathJoin(backupBase, basename(srcPath)), ('.%s' % getTimeString()) if addTimeString else '')
	removePath(tgtPath, backupBase)

	(copy if keepOriginal else os.rename)(srcPath, tgtPath)

	return tgtPath

def restore(backupPath, srcPath=None): #Pending: Add a way to handle time strings. Better yet a make calss for backup (may be as a separate module).
	if not srcPath:
		srcPath = splitext(backupPath)[0]

	_removePath(srcPath)
	os.rename(backupPath, srcPath)

# Init
def setup(Project):
	global fsRoot

	_temp = Project.fsRoot

	fsRoot = abspath(_temp)
	debug('fsRoot: %s' % _temp)

from laufire.initializer import loadProjectSettings #pylint: disable=C0413
loadProjectSettings(setup)
