r"""
A module to help with making the module, filesys, to wotk across platforms.
"""
import platform

# Data
system = platform.system()

if system != 'Windows':
	from os import unlink
	from os.path import isdir, islink

	# Exports
	from os import link, symlink #pylint: disable=W0611

	rmlink = unlink

	def isSymlink(targetPath):
		return isdir(targetPath) and islink(targetPath)

else:
	from os.path import abspath
	from win32com.shell import shell
	from win32file import FILE_ATTRIBUTE_DIRECTORY, GetFileAttributes
	from win32file import CreateHardLink as link, CreateSymbolicLink as symlink, RemoveDirectory as rmlink #pylint: disable=W0611

	# Constants
	FILE_ATTRIBUTE_REPARSE_POINT = 1024
	REPARSE_FOLDER = (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)

	# Exports

	def isSymlink(targetPath):
		r"""Detects whether the given path is a NTFS junction.
		"""
		# #From: http://stackoverflow.com/questions/1447575/symlinks-on-windows
		result = GetFileAttributes(targetPath)
		return result > -1 and result & REPARSE_FOLDER == REPARSE_FOLDER

	# #Pending: Create a standard API for the following functions, across platforms.
	import pythoncom
	import win32con
	from win32api import SetFileAttributes

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
