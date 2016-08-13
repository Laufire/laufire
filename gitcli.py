r"""
gitcli
======

A module to help with git related tasks. It depends upon the availability of the 'git' command through the command line. Existing solutions aren't chosen to save the time to learn.

Notes:

	* **cwd**, **HEAD** and **the current branch** are assumed to be the defaults.
"""
from subprocess import Popen, PIPE
from shlex import split

# Helpers
def call(command, **kwargs): # from gitapi.py
	r"""Executes a shell command and returns its outputs.
	"""
	proc = Popen(split(command), stdout=PIPE, stderr=PIPE, **kwargs)
	out, err = [x.decode("utf-8") for x in proc.communicate()]

	return {'out': out, 'err': err, 'code': proc.returncode}

def getStdout(commandStr, **kwargs):
	r"""Returns the stripped stdout of a successful command.
	"""
	Result = call('git %s' % commandStr, **kwargs)

	if Result['code'] != 0:
		raise Exception(Result['err'])

	return Result['out'].strip()

# Exports

# Low level calls
def command(commandStr, cwd='.'):
	r"""Executes a git command and returns its outputs.
	"""
	return call('git %s' % commandStr, cwd=cwd)

def lines(commandStr, cwd='.'):
	r"""Executes a git command and returns its stdout lines as a list.
	"""
	Result = call('git %s' % commandStr, cwd=cwd)

	if Result['code']:
		errStr = Result['err'].strip()
		raise(Exception(errStr[:errStr.find('\n')]))

	out = Result['out'].strip()

	return out.split('\n') if out else []

# Info
def isClean(dir=None):
	r"""Ensures that the given dir doesn't have any uncommited changes.
	"""
	return getStdout('status "%s" --porcelain' % (dir or getRepoPath())) == ''

def getCommitMessage():
	r"""Returns the commit message of the last commit of the current branch.
	"""
	return getStdout('log -1 --pretty=%B').strip()

def getCommmitId():
	r"""Returns the commit id of the last commit of the current branch.
	"""
	return getStdout('rev-parse HEAD').strip()

def getCurrentBranch():
	r"""Returns the name of the current branch.
	"""
	return getStdout('rev-parse --abbrev-ref HEAD').strip()

def getFileList(dir='.'):
	r"""Returns the list of gitted files under the given dir.
	"""
	return getStdout('ls-files', cwd=dir).split('\n')

def getRepoPath():
	return getStdout('rev-parse --show-toplevel').strip()

def isExportable():
	r"""Ensures that the current state of the repo is clean and of the master branch.
	"""
	return isClean(getRepoPath()) and getCurrentBranch() == 'master'

# Tagging
def getTags(pattern=None):
	r"""Returns the list of tags from the current branch.
	"""
	return lines('tag%s' % ('' if not pattern else ' -l "%s"' % pattern))

def addTag(tagName, tgtTreeish=None):
	getStdout('tag "%s"%s' % (tagName, '' if not tgtTreeish else (' "%s"' % tgtTreeish)))

def deleteTag(tagName):
	getStdout('tag -d "%s"' % tagName)

# Utilities

def archive(archiveTarget, pathToArchive='.', treeish='HEAD'):
	r"""Archives the pathToArchive of the given treeish, to the archiveTarget.
	"""
	assert(command('archive --format=zip --output "%s" %s' % (archiveTarget, treeish), cwd=pathToArchive)['code'] == 0)
