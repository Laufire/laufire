r"""
FileSys
=======

	A module to help with files system operations.

Notes
-----

	* Path removals generally require an ancestor to be specified, so to avoid accidental deletes.
	* Unlike removals, replacements (like copy, makeLink etc) doesn't require an ancestor, as the possibilty of loss is little (as most replacements, practically occur in creating recreatable resources).
	* The module shutill isn't used as it treats file-system differently, than this module does. Ex: shutil.rmtree will remove the files with-in dir junctions instead of merely removing the junction.

Pending
-------

	* Check: Could links be removed, even outside the fsRoot?
	* Support file encodings.
	* Add a function to copy file attributes, etc.
	* Add an isOk call to verify the correctness of the files (to avoid unresolved links etc).
	* Use absPaths for robustness of the calls.
"""

import os
import fnmatch
import re

from os import mkdir, makedirs, unlink, rmdir
from os.path import abspath, basename, commonprefix, dirname, exists, isdir, isfile, join as pathJoin, normpath, split as pathSplit, splitext

from laufire.logger import debug
from laufire.utils import getRandomString, getTimeString
from laufire.helpers.filesys import link, symlink, rmlink, isLinkedDir

from glob2 import glob

# State
fsRoot = '.' # Risky filesystem operations such as removePath are limited to fsRoot.

# Data
Ext2Opener = {'zip': ('zipfile', 'ZipFile'), 'gz': 'gzip'} # #Pending: Instead of having module, object pairs import objects (for that write a support module. ie: import_obj('zipfile.ZipFile')

# Helpers
def rmtree(tgtPath):
	r"""Removes a dir tree. It can unlink junctions (even as sub-dirs), without removing the descendant files.
	"""
	absPath = abspath(tgtPath)

	for root, dirs, Files in os.walk(absPath):
		for file in Files:
			unlink(pathJoin(root, file))

		for dir in dirs:
			dir = pathJoin(root, dir)

			if isLinkedDir(dir):
				rmlink(dir)

			else:
				rmtree(dir)

	rmdir(tgtPath)

def _makeLink(srcPath, tgtPath, pathType, hardLinks):
	if pathType == 1:
		(link if hardLinks else symlink)(abspath(srcPath), abspath(tgtPath))

	else:
		symlink(abspath(srcPath), abspath(tgtPath)) # #Note: Dirs can't be hard-linked.

def _removePath(tgtPath):
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

		else: # a module name and object name pair is available.
			return lambda filePath: getattr(import_module(opener[0]), opener[1])(filePath).open

	else:
		return lambda filePath: open(filePath, 'rb')

def pair(src, tgt, postFix):
	r"""Returns a pair of the given post-fix affixed source and target paths.
	"""
	return '%s/%s' % (src, postFix), '%s/%s' % (tgt, postFix)

def getPathPairs(source, target, *Includes):
	r"""Iterates over the given globs and yields a tuple with source and destination paths.
	"""
	srcLen = len(source) + 1

	for Collection in collectPaths(source, Includes):
		for filePath in ['%s/%s' % (source, item) for item in Collection]:
			yield filePath, '%s/%s' % (target, filePath[srcLen:])

# Exports
def resolve(basePath, relation):
	r"""Resolves a relative path of the given basePath.

	Args:
		basePath (path): The path of the base.
		relation (str): The relation. Ex: '..', '../ops' etc.
	"""
	return abspath(pathJoin(basePath, relation))

def copy(srcPath, tgtPath, overwrite=False):
	r"""Copies one path to the other.
	"""
	srcPath = abspath(srcPath)
	tgtPath = abspath(tgtPath)

	if not overwrite:
		_removePath(tgtPath) # #Note: The target is not removed unless the source is valid.

	ensureParent(tgtPath)

	if getPathType(srcPath) == 1:
		copyContent(srcPath, tgtPath)

	else:
		ensureDir(tgtPath)
		Dirs, Files = collectPaths(srcPath)

		if overwrite:
			for dir in Dirs:
				mkdir('%s/%s' % (tgtPath, dir))

		else:
			for dir in Dirs:
				dir = '%s/%s' % (tgtPath, dir)
				if not exists(dir):
					mkdir(dir)

		for file in Files:
			copyContent(*pair(srcPath, tgtPath, file))

def makeLink(srcPath, tgtPath, hardLinks=False):
	r"""Links two paths. Files are hard linked, where as dirs are linked as junctions.
	"""
	debug('linking: %s => %s' % (srcPath, tgtPath))
	srcPath = abspath(srcPath)
	tgtPath = abspath(tgtPath)

	pathType = getPathType(srcPath)
	_removePath(tgtPath)
	ensureParent(tgtPath)

	_makeLink(srcPath, tgtPath, pathType, hardLinks)

def linkTree(srcPath, tgtPath, Includes=None, Excludes=None, **KWArgs):
	r"""Re-creates the structure of the source at the target by creating dirs and linking files.

	KWArgs:
		hardLinks (boolean): Uses hard links for linking.
		clean (boolean): Cleans the target dir before linking.
	"""
	hardLinks = KWArgs.get('hardLinks', False)

	clean = KWArgs.get('clean', True)

	if clean:
		removePath(tgtPath)

	linker = symlink if not hardLinks else link

	ensureDir(tgtPath)

	Dirs, Files = collectPaths(srcPath, Includes, Excludes)

	for dir in (Dirs if clean else [dir for dir in Dirs if not exists(dir)]):
		mkdir('%s/%s' % (tgtPath, dir))

	_srcPath = abspath(srcPath) # Link sources should be abs-paths.

	for file in Files:
		Pair = pair(_srcPath, tgtPath, file)
		debug('linking: %s => %s' % Pair)

		tgtFilePath = Pair[1]
		ensureParent(tgtFilePath)

		if not clean and exists(tgtFilePath):
			unlink(tgtFilePath)

		linker(*Pair)

def removePath(tgtPath, requiredAncestor=None, forced=False):
	r"""Removes any given file / dir / junction.

	Args:
		tgtPath (path): The path to remove.
		requiredAncestor (path): The target will only be removed if it's a descendant of this dir. Defaults to the global attr fsRoot.
		forced (bool): When set to true, an ancestor won't be required.
	"""
	if not forced:
		tgtPath = abspath(tgtPath)
		requiredAncestor = abspath(requiredAncestor or fsRoot)

		if not isDescendant(tgtPath, requiredAncestor):
			raise Exception('"%s" is not a descendant of "%s"' % (tgtPath, requiredAncestor))

	debug('removePath: %s' % tgtPath)
	return _removePath(tgtPath)

def rename(srcPath, tgtPath, requiredAncestor=None, forced=False):
	r"""Renames any given file / dir / junction.

	Args:
		Args:
		srcPath (path): The path to rename.
		tgtPath (path): The target of the rename.
		requiredAncestor (path): The target will only be renamed if it's a descendant of this dir. Defaults to the global attr fsRoot.
		forced (bool): When set to true, an ancestor won't be required.
	"""
	removePath(tgtPath, requiredAncestor, forced)
	os.rename(srcPath, tgtPath)

def ensureParent(childPath):
	r"""Ensures the parent dir of the given childPathexists.

		This function is provided to ease the use of other file copying tasks.

		#Note: makedirs isn't used, as it doesn't report properly on occupied names.
	"""
	parentPath = dirname(normpath(childPath))
	Paths = []

	while parentPath and not isContainer(parentPath):
		assert not exists(parentPath), 'Parent path is occupied: %s'% parentPath
		Paths.insert(0, parentPath)
		parentPath = dirname(parentPath)

	for path in Paths:
		mkdir(path)

def ensureDir(dir):
	r"""Ensures that the given dir is available.
	"""
	if not exists(dir):
		ensureParent(dir)
		mkdir(dir)

def ensureCleanDir(dir, requiredAncestor=None):
	r"""Ensures that the given dir is clean and available.
	"""
	removePath(dir, requiredAncestor)
	makedirs(dir)

def getFreeFilePath(parentDir, length=8):
	if exists(parentDir):
		while True:
			freePath = pathJoin(parentDir, getRandomString(length))

			if not exists(freePath):
				return freePath

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

def getContent(filePath):
	r"""Reads a file and returns its content.
	"""
	with open(filePath, 'rb') as file:
		content = file.read()

	return content

def iterateContent(filePath, width=4096):
	r"""Reads the given file as small chunks. This could be used to read large files without buffer overruns.
	"""
	with open(filePath, 'rb') as file:
		for chunk in iter(lambda: file.read(width), b''):
			yield chunk

def setContent(filePath, content):
	r"""Fills the given file with the given content.
	"""
	ensureParent(filePath)

	with open(filePath, 'wb') as file:
		file.write(content)

def copyContent(srcPath, tgtPath):
	r"""
	Copies the content of one file to another.

	# #Note: Unlike shutil.copy attributes aren't copied.
	"""
	with open(tgtPath, 'wb') as tgt:
		for chunk in iterateContent(srcPath):
			tgt.write(chunk)

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

def expandGlobs(rootPath, *Patterns):
	r"""Expands a set of patterns for a given rootPath.

	Note:
		rootPath could be a file or a dir.
		('**', '.*', '.*/**', '.*/.**') is the glob pattern for a collection all files.
	"""
	from glob2 import glob

	Paths = []

	if Patterns:
		for pattern in Patterns:
			Paths += glob(pathJoin(rootPath, pattern))

	else: # We haven't got any patterns hence return the rootPath if it exists
		return [rootPath] if exists(rootPath) else []

	return Paths

def collectPaths(base, Includes=None, Excludes=None, regex=False, followlinks=True):
	r"""Returns two lists containing dirs and files of the given base dir.

	Args:
		base (str): The path to scan for.
		Includes (list): A list of globs to include, defaults to all.
		Excludes (list): A list of globs to exclude, defaults to none.
		regex (bool, False): When set to True, Includes and Excludes are parsed as regular expressions, instead of as globs.

	#From: http://stackoverflow.com/questions/5141437/filtering-os-walk-dirs-and-files
	#Note: Includes and Excludes are not regulat globs, as they cant experss 'files at the root' as a single expression. But they do support regular expressions.
	# #Pending: Allow non-nested traversals.
	"""
	if regex:
		includes = r'|'.join(Includes) if Includes else r'.*'
		excludes = r'|'.join(Excludes) if Excludes else r'$.'

	else:
		# transform glob patterns to regular expressions
		includes = r'|'.join([fnmatch.translate(x) for x in Includes]) if Includes else r'.*'
		excludes = r'|'.join([fnmatch.translate(x) for x in Excludes]) if Excludes else r'$.'

	AllDirs = []
	AllFiles = []

	base = base.replace('\\', '/')

	for root, Dirs, Files in os.walk(base, followlinks=followlinks):

		# Exclude dirs.
		Dirs[:] = [d for d in Dirs if not re.match(excludes, d)]
		AllDirs += [(pathJoin(root, d)).replace('\\', '/') for d in Dirs]

		# Exclude / Include files.
		Files = [(pathJoin(root, f)).replace('\\', '/') for f in Files]
		Files = [f for f in Files if not re.match(excludes, f)]
		Files = [f for f in Files if re.match(includes, f)]

		AllFiles += Files

	AllDirs = [d for d in AllDirs if re.match(includes, d)]

	startPos = len(base) + 1
	return [dir[startPos:] for dir in AllDirs], [file[startPos:] for file in AllFiles]

def isDescendant(probableDescendant, requiredAncestor):
	r"""Checks whether the given path is a descendant of another.

	Args:
		requiredAncestor (str): The absolute path of the required ancestor.
		probableDescendant (str): The absolute path of the probable descendant.
	"""
	requiredAncestor = abspath(requiredAncestor)

	return commonprefix([abspath(probableDescendant), requiredAncestor]) == requiredAncestor

def isContainer(path):
	return isdir(path) or isLinkedDir(path)

def getPathType(path):
	ret = 1

	for func in [isfile, isdir, isLinkedDir]:
		if func(path):
			break

		ret += 1

	return ret

def compress(srcPath, tgtPath, overwrite=False): # #Note: shutil.make_archive isn't used, due to its forcing of the zip extension and due to the need for maintaing a compression standard.
	if not exists(srcPath):
		raise('No such path: %s' % srcPath)

	if not overwrite and exists(tgtPath):
		_removePath(tgtPath)

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

def extract(srcPath, tgtPath): # #Note: The tagertPath points to the extraction root, hence it should be a dir.
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

	fsRoot = Project.fsRoot

from laufire.initializer import loadProjectSettings
loadProjectSettings(setup)
