r"""A helper for SSH operations.

#Note: This module needs the SSHConfig to be in Project.Config['SSH']
#Later: Ad support for recursive downloads.
"""
import json
import errno

from os import listdir
from os.path import basename, split as pathSplit

import paramiko
from laufire.extensions import Lazy
from laufire.filesys import getPathType, joinPaths, pair
from laufire.flow import forgive, retry
from laufire.logger import debug
from laufire.shell import assertShell

# Helpers
def _upload(SFTP, localPath, remotePath):

	debug('uploading %s to %s' % (localPath, remotePath))

	pathType = getPathType(localPath)

	if pathType == 1: # file
		retry(lambda: SFTP.put(localPath, remotePath) or 1) # #Note: 1 is returned to notify retry of a success.

	elif pathType > 1: # dir / junction
		err = forgive(lambda: mkdirs(SFTP, remotePath))

		if err and not isinstance(err, IOError):
			raise err

		for item in listdir(localPath): # #Note: With dir uploads, the uploads are merged (added / overwritten) with existing paths.
			retry(lambda: _upload(SFTP, *pair(localPath, remotePath, item))) #pylint: disable=cell-var-from-loop

	else: # Path doesn't exist.
		raise Exception('Invalid source path: %s' % localPath)

	return remotePath

def mkdirs(SFTP, remotePath):
	currentPath = remotePath

	Skipped = []

	while True:
		err = forgive(lambda: SFTP.mkdir(currentPath, 511)) # #Note: Existense isn't checked for to reduce the number of remote calls.

		if err:
			if err.errno is None: # The dir exists.
				return

			elif not isinstance(err, IOError): # #Pending: Check: Permission errors could result in infinite loops.
				raise err

			else:
				# Try to create the parent path.
				currentPath, skipped = pathSplit(currentPath)
				Skipped.append(skipped)

				if not currentPath or currentPath == '/':
					raise Exception('Failed to create the dir: %s' % remotePath)

		else:
			if not Skipped:
				break

			else:
				currentPath += '/%s' % Skipped.pop(0)

def getTgtName(tgtName, srcPath):
	return tgtName if tgtName else basename(srcPath)

# Classes
class SSHClient(paramiko.SSHClient):
	r"""An abstraction layer over the SSH client.
	"""
	def __init__(self, SSHConfig):
		paramiko.SSHClient.__init__(self)

		self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.load_system_host_keys()
		self.connect(SSHConfig['host'], username=SSHConfig['username'], password=SSHConfig['password'])
		self._SFTP = self.open_sftp()

	def __del__(self):
		self._SFTP.close()

	def __getattr__(self, attr):
		r"""
		Allows to access the methods of the underlying SFTP connection.
		"""
		return getattr(self._SFTP, attr)

	def download(self, remotePath, localPath=''):
		debug('downloading %s to %s' % (remotePath, localPath))
		SFTP = self.open_sftp()
		localPath = getTgtName(localPath, remotePath)
		SFTP.get(remotePath, localPath)
		SFTP.close()

		return localPath

	def upload(self, localPath, remotePath):
		remotePath = getTgtName(remotePath, localPath)

		SFTP = self.open_sftp()
		_upload(SFTP, localPath, remotePath)
		SFTP.close()

		return remotePath

	def exists(self, path):
		err = forgive(lambda: self._SFTP.stat(path))

		return True if not err else (isinstance(err, IOError) and err.errno == errno.ENOENT)

	def execute(self, command):
		debug(command)
		dummy, stdout, stderr = self.exec_command(command)

		return {

			'code': stdout.channel.recv_exit_status(),
			'out': stdout.read(),
			'err': stderr.read(),
		}

class SSHBridge:
	r"""Bridges with the SSH gateway of the remote host.
	"""
	def __init__(self, Config):
		self.Config = Config
		self.Client = Lazy(SSHClient, Config['SSH']) # #Note: SSHBridge is initialized as lazy class, as parmiko cannot connect to the server when modules are being loaded, due to some internals of threading.

	def __getattr__(self, attr):
		r"""
		Allows access to the methods of the underlying client.
		"""
		return getattr(self.Client, attr)

	def iexecute(self, command):
		r"""Interpolates the command with the Config, before executing.
		"""
		return self.Client.execute(command.format(**self.Config['Gateway']))

	def callScript(self, ecCommand):
		out = assertShell(self.iexecute('{Python[binary]} {Paths[private]}/%s' % ecCommand))
		return json.loads(out) if out else None

	def upload(self, srcPath, tgtPath=''):
		r"""Uploads through the gateway are done to the temp dir by default.
		"""
		if not tgtPath:
			tgtPath = joinPaths(self.Config['Gateway']['Paths']['temp'], getTgtName(None, srcPath))

		else:
			tgtPath = tgtPath.format(**self.Config['Gateway'])

		return self.Client.upload(srcPath, tgtPath)
