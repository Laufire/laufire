r"""
A module to help with development.
"""
import json

from laufire.dev import getPretty
from laufire.filesys import basename, copy, ensureParent, joinPaths
from laufire.flow import rob
from laufire.logger import debug
from laufire.shell import call, debugCall, assertShell

# Helpers
def getTgtName(tgtName, srcPath):
	return tgtName if tgtName else basename(srcPath)

class SSHClientMocker:
	def __init__(self, Config):
		Paths = Config['Gateway']['Paths']
		self.mockBase = Paths['base']

	def execute(self, command, **KWArgs):
		return call(command, **KWArgs)

	def upload(self, srcPath, tgtPath): # #Note: Uploads are done always to the temp dir.
		debug('uploading %s -> %s' % (srcPath, tgtPath))
		ensureParent(tgtPath)
		return copy(srcPath, tgtPath)

# Exports
class SSHBridgeMocker:
	r"""A class to help with the development of gateway scripts, by executing the commands locally.

	# #Note: This class doesn't fully mock SSHBridge as the need didn't arise.
	"""
	def __init__(self, Config):
		self.Config = Config
		self.Client = SSHClientMocker(Config)

		Config['Gateway']['Python']['binary'] = 'python' # #Pending: This is a quick fix. Remove it, once the remote can locate its python through shell.

		self.mockScriptTpl = '%s %s/%%s' % (Config['Gateway']['Python']['binary'], Config['Gateway']['Paths']['private'])

	def __getattr__(self, attr):
		r"""
		Allows the access of the methods of the Client.
		"""
		return getattr(self.Client, attr)

	def iexecute(self, command, **KWArgs):
		r"""Interpolates the command with the Config, before executing.
		"""
		return self.Client.execute(command.format(**self.Config['Gateway']), **KWArgs)

	def callScript(self, ecCommand):
		out = assertShell(call(self.mockScriptTpl % ecCommand, shell=True))

		if out:
			Out =	rob(lambda: json.loads(out))

			if Out is None:
				raise Exception(out)

			debug(getPretty(Out))
			return Out

	def debugScript(self, ecCommand):
		r"""Helps with debugging the gateway scripts.
		"""
		debugCall(self.mockScriptTpl % ecCommand)

	def upload(self, srcPath, tgtPath=''):
		if not tgtPath:
			tgtPath = joinPaths(self.Config['Gateway']['Paths']['temp'], getTgtName(None, srcPath))

		else:
			tgtPath = tgtPath.format(**self.Config['Gateway'])

		return self.Client.upload(srcPath, tgtPath)
