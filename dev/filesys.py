r"""
FileSys
=======

	A module to help with files system operations.

# #Note: Path removals generally require an ancestor to be specified, so to avoid accidental deletes.
# #Note: Unlike removals, replacements (like copy, makeLink etc) doesn't require an ancestor, as the possibilty of loss is little (as most replacements, practically occur in creating recreatable resources).

#Pending: Support file encodings.
"""
import os
import fnmatch
import re

from os import unlink, rmdir, makedirs
from os.path import isdir, isfile, split as pathSplit, abspath, join as pathJoin, exists, dirname, basename, commonprefix, splitext
from glob2 import glob
from shutil import copy as _copy, copytree

from laufire.logger import debug
from laufire.utils import getRandomString, getTimeString

from laufire.helpers.filesys import link, symlink, rmlink, isLinkedDir

# State
fsRoot = '.' # Risky filesystem operations such as removePath are limited to fsRoot.

# Data
Ext2Opener = {'zip': ('zipfile', 'ZipFile'), 'gz': 'gzip'} # #Pending: Instead of having module, object pairs import objects (for that write a support module. ie: import_obj('zipfile.ZipFile')
_AllFiles = ['**/*.*', '**/.*']

# Helpers
def rmtree(targetPath):
	r"""Removes a dir tree. It can unlink junctions (even as sub-dirs), without removing the descendant files.
	"""
	absPath = abspath(targetPath)

	for root, dirs, Files in os.walk(absPath):
		for file in Files:
			unlink(pathJoin(root, file))

		for dir in dirs:
			dir = pathJoin(root, dir)

			if isLinkedDir(dir):
				rmlink(dir)

			else:
				rmtree(dir)

	rmdir(targetPath)

def _removePath(targetPath):
	if isfile(targetPath):
		unlink(targetPath)

	elif isLinkedDir(targetPath):
		rmlink(targetPath)

	elif isdir(targetPath):
		rmtree(targetPath)

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

def getPathPairs(source, target, *Globs):
	r"""Iterates over the given globs and yields a tuple with source and destination paths.
	"""
	srcLen = len(source) + 1

	for item in Globs:
		for filePath in glob('%s/%s' % (source, item)):
			yield filePath, '%s/%s' % (target, filePath[srcLen:])

# Exports
def resolve(basePath, relation):
	r"""Resolves a relative path of the given basePath.

	Args:
		basePath (path): The path of the base.
		relation (str): The relation. Ex: '..', '../ops' etc.
	"""
	return abspath(pathJoin(basePath, relation))

def copy(sourcePath, targetPath):
	r"""Copies one path to the other.
	"""
	sourcePath = abspath(sourcePath)
	targetPath = abspath(targetPath)

	if isfile(sourcePath):
		_removePath(targetPath) # #Note: The target is not removed unless the source is valid.
		ensureParent(targetPath)
		_copy(sourcePath, targetPath)

	elif isContainer(sourcePath):
		_removePath(targetPath)
		ensureParent(targetPath)
		copytree(sourcePath, targetPath)

	else:
		raise Exception('Invalid source path: %s' % sourcePath)

def makeLink(sourcePath, targetPath, isHard=False):
	r"""Links two paths. Files are hard linked, where as dirs are linked as junctions.
	"""
	debug('linking: %s => %s' % (sourcePath, targetPath))
	sourcePath = abspath(sourcePath)
	targetPath = abspath(targetPath)

	if isfile(sourcePath):
		_removePath(targetPath)
		ensureParent(targetPath)
		(link if isHard else symlink)(sourcePath, targetPath)

	elif isContainer(sourcePath):
		_removePath(targetPath)
		ensureParent(targetPath)

		symlink(sourcePath, targetPath) # #Note: Dirs can't be hard-linked.

	else:
		raise Exception('Invalid source path: %s' % sourcePath)

def linkTree(source, target, *Globs, **KWArgs):
	r"""Re-creates the structure of the source at the target by creating dirs and linking files.

	KWArgs:
		hardLinks (boolean): Uses hard links for linking.
		clean (boolean): Cleans the target dir before linking.
	"""
	hardLinks = KWArgs.get('hardLinks', False)

	if not Globs:
		Globs = _AllFiles

	if KWArgs.get('clean'):
		removePath(target)

	for src, dest in getPathPairs(source, target, *Globs):
		ensureParent(dest)
		makeLink(src, dest, hardLinks)

def removePath(targetPath, requiredAncestor=None, forced=False):
	r"""Removes any given file / dir / junction.

	Args:
		targetPath (path): The path to remove.
		requiredAncestor (path): The target will only be removed if it's a descendant of this dir. Defaults to the global attr fsRoot.
		forced (bool): When set to true, an ancestor won't be required.
	"""
	if not forced:
		targetPath = abspath(targetPath)
		requiredAncestor = abspath(requiredAncestor or fsRoot)

		if not isDescendant(targetPath, requiredAncestor):
			raise Exception('"%s" is not a descendant of "%s"' % (targetPath, requiredAncestor))

	debug('removePath: %s' % targetPath)
	return _removePath(targetPath)

def rename(sourcePath, targetPath, requiredAncestor=None, forced=False):
	r"""Renames any given file / dir / junction.

	Args:
		Args:
		sourcePath (path): The path to rename.
		targetPath (path): The target of the rename.
		requiredAncestor (path): The target will only be renamed if it's a descendant of this dir. Defaults to the global attr fsRoot.
		forced (bool): When set to true, an ancestor won't be required.
	"""
	removePath(targetPath, requiredAncestor, forced)
	os.rename(sourcePath, targetPath)

def ensureParent(childPath):
	r"""Ensures the parent dir of the given childPathexists.

		This function is provided to ease the use of other file copying tasks.
	"""
	parentPath = dirname(childPath)

	if not exists(parentPath):
		makedirs(parentPath)

def ensureDir(dir):
	r"""Ensures that the given dir is available.
	"""
	if not exists(dir):
		makedirs(dir)

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
	with open(filePath, 'wb') as file:
		file.write(content)

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
	"""
	Paths = []

	if Patterns:
		for pattern in Patterns:
			Paths += glob(pathJoin(rootPath, pattern))

	else: # We haven't got any patterns hence return the rootPath if it exists
		return [rootPath] if exists(rootPath) else []

	return Paths

def collectPaths(base, Includes=None, Excludes=None, absPaths=False, regex=False, followlinks=True):
	r"""Returns two lists containing dirs and files of the given base dir.

	Args:
		base (str): The path to scan for.
		Includes (list): A list of globs to include, defaults to all.
		Excludes (list): A list of globs to exclude, defaults to none.
		absPaths (bool, False): When set to True, returns the result as absolute paths.
		regex (bool, False): When set to True, Includes and Excludes are parsed as regular expressions, instead of as globs.

	#From: http://stackoverflow.com/questions/5141437/filtering-os-walk-dirs-and-files
	# #Pending: Allow non-nested taraversals.
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

	if not absPaths:
		startPos = len(base) + 1
		return [dir[startPos:] for dir in AllDirs], [file[startPos:] for file in AllFiles]

	else:
		return AllDirs, AllFiles

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
	ret = 0

	for func in [isfile, isdir, isLinkedDir]:
		ret += 1

		if func(path):
			break

	return ret

def compress(sourcePath, targetPath): # #Note: shutil.make_archive isn't used, due to its forcing of the zip extension and due to the need for maintaing a compression standard.
	if not exists(sourcePath):
		raise('No such path: %s' % sourcePath)

	if exists(targetPath):
		_removePath(targetPath)

	from zipfile import ZipFile, ZIP_DEFLATED

	ZipFileObj = ZipFile(targetPath, 'w', ZIP_DEFLATED)

	cwd = os.getcwd() # The CWD circus is to reduce the relpath calls.

	if isContainer(sourcePath):
		os.chdir(sourcePath)

		for root, dummy1, Files in os.walk('.', followlinks=True):
			for file in Files:
				ZipFileObj.write(pathJoin(root, file))

	else:
		dir, name = pathSplit(sourcePath)
		os.chdir(dir)

		ZipFileObj.write(name)

	os.chdir(cwd)

	ZipFileObj.close()

def extract(sourcePath, targetPath): # #Note: The tagertPath points to the extraction root, hence it should be a dir.
	from zipfile import ZipFile

	with ZipFile(sourcePath, 'r') as Z:
		Z.extractall(targetPath)

def backup(sourcePath, backupBase=None, addTimeString=True, keepOriginal=False): # #Pending: Change the name of the call to preserve or safeguard. As the current name could be misleading.
	r"""Backs up the given path to a temporary location, so that the returned path could be later used to restore it to the original location.

	When backupBase isn't given the path is renamed, not moved.
	# #Note: This call along with restore, could preserve links.
	"""
	if not backupBase:
		backupBase = dirname(abspath(sourcePath))

	targetPath = '%s%s.bak' % (pathJoin(backupBase, basename(sourcePath)), ('%s.' % getTimeString()) if addTimeString else '')
	removePath(targetPath, backupBase)

	(copy if keepOriginal else os.rename)(sourcePath, targetPath)

	return targetPath

def restore(backupPath, sourcePath=None): #Pending: Add a way to handle time strings. Better yet a make calss for backup (may be as a separate module).
	if not sourcePath:
		sourcePath = splitext(backupPath)[0]

	_removePath(sourcePath)
	os.rename(backupPath, sourcePath)

# Init
def setup(Project):
	global fsRoot

	fsRoot = Project.fsRoot

from laufire.initializer import loadProjectSettings
loadProjectSettings(setup)
