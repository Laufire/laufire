r"""A helper for SSH operations.

#Note: This module needs the SSHConfig to be in Project.Config['SSH']
#Later: Ad support for recursive downloads.
"""
import json
import errno

from os import listdir
from os.path import basename, split as pathSplit
from re import compile, sub

import paramiko
from laufire.extensions import Lazy
from laufire.flow import forgive
from laufire.filesys import getPathType
from laufire.logger import debug
from laufire.shell import assertShell

# Data
homeDirPatern = compile(r'^~/')

# Helpers
def expandPath(path, homeDir):
	return sub(homeDirPatern, '%s/' % homeDir, path)

def _upload(SFTP, localPath, remotePath):

	debug('uploading %s to %s' % (localPath, remotePath))

	pathType = getPathType(localPath)

	if pathType == 1: # file
		SFTP.put(localPath, remotePath)

	elif pathType > 1: # dir / junction
		err = forgive(lambda: mkdirs(SFTP, remotePath))

		if err and not isinstance(err, IOError):
			raise err

		for item in listdir(localPath): # #Note: With dir uploads, the uploads are merged (added / overwritten) with existing paths.
			_upload(SFTP, '%s/%s' % (localPath, item), '%s/%s' % (remotePath, item))

	else: # Path doesn't exist.
		raise Exception('Invalid source path: %s' % localPath)

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

class SSHClient(paramiko.SSHClient):
	r"""An abstraction layer over the SSH client.
	"""
	def __init__(self, SSHConfig):
		paramiko.SSHClient.__init__(self)

		self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.load_system_host_keys()
		self.connect(SSHConfig['host'], username=SSHConfig['username'], password=SSHConfig['password'])

		self._homeDir = self.execute('echo ~')['out'].strip()

		self._SFTP = self.open_sftp()

	def __del__(self):
		self._SFTP.close()

	def __getattr__(self, attr):
		r"""
		Allows the access of the methods of the underlying SFTP connection.
		"""
		return getattr(self._SFTP, attr)

	def download(self, remotePath, localPath=''):
		debug('downloading %s to %s' % (remotePath, localPath))
		SFTP = self.open_sftp()
		SFTP.get(expandPath(remotePath, self._homeDir), getTgtName(localPath, remotePath))
		SFTP.close()

	def upload(self, localPath, remotePath):
		remotePath = getTgtName(remotePath, localPath)
		debug('uploading %s to %s' % (localPath, remotePath))
		SFTP = self.open_sftp()
		_upload(SFTP, localPath, expandPath(remotePath, self._homeDir))
		SFTP.close()

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
		self.GatewayConfig = Config['Gateway']
		self.Client = Lazy(SSHClient, Config['SSH']) # #Note: SSHBridge is initialized as lazy class, as parmiko cannot connect to the server when modules are being loaded, dur to some internals of threading.

	def execute(self, command):
		return self.Client.execute(command)

	def iexecute(self, command):
		r"""Interpolates the command with the Config, before executing.
		"""
		return self.Client.execute(command.format(**self.GatewayConfig))

	def callScript(self, ecCommand):
		out = assertShell(self.iexecute('cd {appDir} && {pythonPath} %s' % ecCommand))
		return json.loads(out) if out else None

	def upload(self, srcPath, tgtName=''): # #Note: Uploads are always done to the temp dir.
		return self.Client.upload(srcPath, '%s/%s' % ('~/gateway/_temp', getTgtName(tgtName, srcPath)))
