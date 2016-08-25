r"""
A module to help with debelopment.
"""
import json

from laufire.filesys import copy, ensureParent
from laufire.logger import debug
from laufire.shell import call, debugCall, assertShell
from laufire.ssh import getTgtPath

class SSHBridgeMocker:
	r"""A class to help with the development of gateway scripts, by executing the commands locally.

	# #Note: This class doesn't fully mock SSHBridge as the need didn't arise.
	"""
	def __init__(self, Config):
		MockConfig = Config['Gateway']['Mock']
		self.GatewayConfig = Config['Gateway']
		self.mockScriptTpl = MockConfig['scriptTemplate']
		self.mockBase = MockConfig['base']

	def callScript(self, ecCommand):
		out = assertShell(call(self.mockScriptTpl % ecCommand, cwd=self.mockBase))
		debug(out)
		return json.loads(out) if out else None

	def debugScript(self, ecCommand):
		r"""Helps with debugging the gateway scripts.
		"""
		debugCall(self.mockScriptTpl % ecCommand, cwd=self.mockBase)

	def upload(self, srcPath, tgtPath=''): # #Note: Uploads are done always to the temp dir.
		tgtPath = '%s/%s/%s' % (self.mockBase, self.GatewayConfig['Paths']['temp'], getTgtPath(tgtPath, srcPath))
		ensureParent(tgtPath)
		return copy(srcPath, tgtPath)
