r"""
A module to help with debelopment.
"""
import json
import re

from laufire.dev import getPretty
from laufire.filesys import abspath, copy, ensureParent
from laufire.flow import rob
from laufire.logger import debug
from laufire.shell import call, debugCall, assertShell
from laufire.ssh import getTgtName

# Helpers
def getTgtName(tgtName, srcPath):
	return tgtName if tgtName else basename(srcPath)

class SSHClientMocker:
	def __init__(self, Config):
		MockConfig = Config['Gateway']['Mock']
		self.GatewayConfig = Config['Gateway']
		self.mockScriptTpl = MockConfig['scriptTemplate']
		self.mockBase = MockConfig['base'] # #Pending: Stel the CWD before execution and if possible restore it.
		self.gatewayDir = MockConfig['gateway']

		Config['Gateway']['pythonPath'] = 'python' # #Pending: This is a puick fix. Remove it, once the remote can locate its python thrugh shell.

	def _expandPath(self, tgtPath, useAbsPath=False):
		return tgtPath.replace('~', abspath(self.mockBase) if useAbsPath else self.mockBase) # #Caution: This is a corase implementation, as os.path.expandvars couldn't be used on a remote system to expand path vars. And using regex is not effective enough.

	def execute(self, command, **KWArgs):
		return call(self._expandPath(command, True), **KWArgs)

	def iexecute(self, command, **KWArgs):
		r"""Interpolates the command with the Config, before executing.
		"""
		return self.execute(command.format(**self.GatewayConfig), **KWArgs)

	def upload(self, srcPath, tgtPath): # #Note: Uploads are done always to the temp dir.
		tgtPath = self._expandPath(tgtPath)
		debug('Uploading %s -> %s' % (srcPath, tgtPath))
		ensureParent(tgtPath)
		return copy(srcPath, tgtPath)

# Exports
class SSHBridgeMocker:
	r"""A class to help with the development of gateway scripts, by executing the commands locally.

	# #Note: This class doesn't fully mock SSHBridge as the need didn't arise.
	"""
	def __init__(self, Config):
		self.Client = SSHClientMocker(Config)

	def __getattr__(self, attr):
		r"""
		Allows the access of the methods of the Client.
		"""
		return getattr(self.Client, attr)

	def callScript(self, ecCommand):
		out = assertShell(call(self.mockScriptTpl % ecCommand, cwd=self.gatewayDir, shell=True))

		if out:
			Out =	rob(lambda: json.loads(out))

			if Out is None:
				raise Exception(out)

			debug(getPretty(Out))
			return Out

	def debugScript(self, ecCommand):
		r"""Helps with debugging the gateway scripts.
		"""
		debugCall(self.mockScriptTpl % ecCommand, cwd=self.gatewayDir)

	def upload(self, srcPath, tgtName=''):
		return self.Client.upload(srcPath, '%s/%s' % ('~/gateway/_temp', getTgtName(tgtName, srcPath)))
