r"""A helper for SSH operations.

#Note: This module needs the SSHConfig to be in Project.Config['SSH']
"""
import json

from os.path import basename
from re import compile, sub

import paramiko
from laufire.extensions import Lazy
from laufire.logger import debug
from laufire.shell import assertShell
from laufire.yamlex import YamlEx

from Project import Config, gatewayConfigPath

# Data
homeDirPatern = compile(r'^~/')
GatewayConfig = YamlEx(gatewayConfigPath, loglevel='ERROR').interpolate()

# Helpers
def expandPath(path, homeDir):
	return sub(homeDirPatern, '%s/' % homeDir, path)

def getTgtPath(tgtPath, srcPath):
	return tgtPath if tgtPath else basename(srcPath)

class SSHClient:
	r"""Bridges with the SSH gateway of the remote host.
	"""
	def __init__(self, SSHConfig):
		self._SSH = SSH = paramiko.SSHClient()
		SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		SSH.load_system_host_keys()
		SSH.connect(SSHConfig['host'], username=SSHConfig['username'], password=SSHConfig['password'])

		self._homeDir = self.execute('echo ~')['out'].strip()

	def download(self, remotePath, localPath=''):
		SFTP = self._SSH.open_sftp()
		SFTP.get(expandPath(remotePath, self._homeDir), getTgtPath(localPath, remotePath))
		SFTP.close()

	def upload(self, localPath, remotePath):
		SFTP = self._SSH.open_sftp()
		SFTP.put(localPath, expandPath(remotePath, self._homeDir))
		SFTP.close()

	def execute(self, command):
		debug(command)
		dummy, stdout, stderr = self._SSH.exec_command(command)

		return {

			'code': stdout.channel.recv_exit_status(),
			'out': stdout.read(),
			'err': stderr.read(),
		}

class SSHBridge:
	r"""An abstraction layer over the SSH client.
	"""
	def __init__(self, SSHConfig):
		self._ = SSHClient(SSHConfig)

	def execute(self, command):
		return self._.execute(command)

	def iexecute(self, command):
		r"""Interpolates the command with the Config, before executing.
		"""
		return self._.execute(command.format(**GatewayConfig))

	def callScript(self, ecCommand):
		out = assertShell(Gateway.iexecute('{pythonPath} {scriptsDir}/%s' % ecCommand))
		return json.loads(out) if out else None

	def upload(self, srcPath, tgtPath=''): # #Note: Uploads are done always to the temp dir.
		return self._.upload(srcPath, '%s/%s' % (GatewayConfig['tempDir'], getTgtPath(tgtPath, srcPath)))

# Delegates
Gateway = Lazy(SSHBridge, Config['SSH']) # #Note: SSHBridge is initialized as lazy class, as parmiko cannot connect to the server when modules are being loaded, dur to some internals of threading.
