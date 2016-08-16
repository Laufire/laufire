import os
import fnmatch
import re

from os import unlink, rmdir, sep as os_sep, makedirs
from os.path import isdir, isfile, split as pathSplit, abspath, join as pathJoin, exists, dirname, normpath
from glob2 import glob
from shutil import copy as _copy, copytree

import win32con
import pythoncom

from win32file import CreateHardLink, RemoveDirectory, CreateSymbolicLink
from win32api import SetFileAttributes
from win32com.shell import shell
from laufire.extensions import namespace
from laufire.utils import getRandomString

# State
fsRoot = abspath('.') # Risky filesystem operations such as removePath are limited to this dir.

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

			if isjunction(dir):
				RemoveDirectory(dir)

			else:
				rmtree(dir)

	rmdir(targetPath)

def _removePath(targetPath):
	if isfile(targetPath):
		unlink(targetPath)

	elif isjunction(targetPath):
		RemoveDirectory(targetPath)

	elif isdir(targetPath):
		rmtree(targetPath)

	else:
		return 1 # error

# Exports
def relpath(basePath, relation):
	r"""Resolves a relative path of the given basePath.

	Args:
		basePath (path): The path of the base.
		relation (str): The relation. Ex: '..', '../ops' etc.
	"""
	return abspath(pathJoin(pathSplit(basePath)[0], relation))

def copy(sourcePath, targetPath):
	r"""Copies one path to the other.
	"""
	sourcePath = abspath(sourcePath)
	targetPath = abspath(targetPath)

	if isfile(sourcePath):
		_copy(sourcePath, targetPath)

	elif isdir(sourcePath):
		_removePath(targetPath)
		copytree(sourcePath, targetPath)

	else:
		raise Exception('Invalid source path: %s' % sourcePath)

def makeLink(sourcePath, targetPath):
	r"""Links two paths. Files are hard linked, where as dirs are linked as junctions.
	"""
	sourcePath = abspath(sourcePath)
	targetPath = abspath(targetPath)

	if isfile(sourcePath):
		if isfile(targetPath):
			unlink(targetPath)

		CreateHardLink(targetPath, sourcePath)

	elif isdir(sourcePath):
		if isjunction(targetPath):
			RemoveDirectory(targetPath)

		elif isdir(targetPath):
			rmdir(targetPath)

		CreateSymbolicLink(targetPath, sourcePath, 1)

	else:
		raise Exception('Invalid source path: %s' % sourcePath)

def removePath(targetPath, requiredAncestor=fsRoot, forced=False):
	r"""Removes any given file / dir / junction.

	Args:
		targetPath (path): The path to remove.
		requiredAncestor (path): The target will only be removed if it's a descendant of this dir. Defaults to the global attr fsRoot.
		forced (bool): When set to true, an ancestor won't be required.
	"""
	if not forced:
		absPath = abspath(targetPath)
		requiredAncestor = abspath(requiredAncestor)

		if not isdescendant(absPath, requiredAncestor):
			raise Exception('"%s" is not a descendant of "%s"' % (absPath, requiredAncestor))

	return _removePath(targetPath)

def ensureParent(childPath):
	r"""Ensures the parent dir of the given childPathexists.

		This function is provided to ease the use of other file copying tasks.
	"""
	parentPath = dirname(childPath)

	if not exists(parentPath):
		makedirs(parentPath)

def ensureCleanDir(dir, requiredAncestor=fsRoot):
	r"""Ensures that the given dir is clean and available.
	"""
	removePath(dir, requiredAncestor)
	makedirs(dir)

def getFreeFilePath(paretnDir, length=8):
	if exists(paretnDir):
		while True:
			freePath = pathJoin(paretnDir, getRandomString(length))

			if not exists(freePath):
				return freePath

def getContent(filePath):
	r"""Reads a file and returns its content.
	"""
	with open(filePath, 'rb') as file:
		content = file.read()

	return content

def setContent(filePath, content):
	r"""Fills the given file with the given content.
	"""
	with open(filePath, 'wb') as file:
		file.write(content)

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

def collectPaths(base, Includes=None, Excludes=None, absPaths=False, regex=False):
	r"""Returns two lists containing dirs and files of the given base dir.

	Args:
		base (str): The path to scan for.
		Includes (list): A list of globs to include, defaults to all.
		Excludes (list): A list of globs to exclude, defaults to none.
		absPaths (bool, False): When set to True, returns the result as absolute paths.
		regex (bool, False): When set to True, Includes and Excludes are parsed as regular expressions, instead of as globs.

	#From: http://stackoverflow.com/questions/5141437/filtering-os-walk-dirs-and-files
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

	for root, Dirs, Files in os.walk(base):

		# Exclude dirs.
		Dirs[:] = [d for d in Dirs if not re.match(excludes, d)]
		AllDirs += [('%s/%s' % (root, d)).replace('\\', '/') for d in Dirs]

		# Exclude / Include files.
		Files = [('%s/%s' % (root, f)).replace('\\', '/') for f in Files]
		Files = [f for f in Files if not re.match(excludes, f)]
		Files = [f for f in Files if re.match(includes, f)]

		AllFiles += Files

	if not absPaths:
		startPos = len(base) + 1
		return [dir[startPos:] for dir in AllDirs], [file[startPos:] for file in AllFiles]

	else:
		return AllDirs, AllFiles

def createShortcut(toDocPath, fromLinkPath):
	shortcut = pythoncom.CoCreateInstance(
		shell.CLSID_ShellLink,
		None,
		pythoncom.CLSCTX_INPROC_SERVER, #pylint: disable=E1101
		shell.IID_IShellLink
		)

	shortcut.SetPath(abspath(toDocPath))

	persistFile = shortcut.QueryInterface(pythoncom.IID_IPersistFile) #pylint: disable=E1101
	persistFile.Save(abspath(fromLinkPath), 0)

def setAttrs(target, *Attrs):
	r"""Sets the given attributes to the given target.

	Args:
		target  (path): The target path to set the attributes.
		*Attrs : One or more attribute names of the `SetFileAttributes <https://msdn.microsoft.com/en-us/library/windows/desktop/aa365535(v=vs.85).aspx>`_ function without the preceeding *FILE_ATTRIBUTE_*.
	"""
	attr = 0
	for item in Attrs:
		attr = attr | getattr(win32con, 'FILE_ATTRIBUTE_%s' % item.upper())

	SetFileAttributes(target, attr)

@namespace
def isjunction():
	r"""Detects whether the given path is a NTFS junction.
	"""
	# #From: http://stackoverflow.com/questions/1447575/symlinks-on-windows
	from win32file import FILE_ATTRIBUTE_DIRECTORY, GetFileAttributes

	FILE_ATTRIBUTE_REPARSE_POINT = 1024
	REPARSE_FOLDER = (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)

	def worker(fpath):
		result = GetFileAttributes(fpath)

		return result > -1 and result & REPARSE_FOLDER == REPARSE_FOLDER

	return worker

def isdescendant(probableDescendant, requiredAncestor):
	r"""Checks whether the given path is a descendant of another.

	Args:
		requiredAncestor (str): The absolute path of the required ancestor.
		probableDescendant (str): The absolute path of the probable descendant.
	"""
	return normpath(probableDescendant).find(normpath(requiredAncestor + os_sep)) == 0
