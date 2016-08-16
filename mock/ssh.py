r"""
A module to help with debelopment.
"""
import json

from laufire.filesys import copy
from laufire.logger import debug
from laufire.shell import call, debugCall, assertShell
from laufire.ssh import GatewayConfig, getTgtPath

MockConfig = GatewayConfig['Mock']
mockTempDir = MockConfig['tempDir']
mockScriptTpl = MockConfig['scriptTemplate']
scriptsDir = MockConfig['scriptsDir']

class SSHBridgeMocker:
	r"""A class to help with the dvelopment of gateway scripts, by passing the commands to them instead of their remote peers.
	"""
	def callScript(self, ecCommand):
		out = assertShell(call(mockScriptTpl % ecCommand))
		debug(out)
		return json.loads(out) if out else None

	def debugScript(self, ecCommand):
		r"""Helps with debugging the gateway scripts.
		"""
		debugCall(mockScriptTpl % ecCommand)

	def upload(self, srcPath, tgtPath=''): # #Note: Uploads are done always to the temp dir.
		return copy(srcPath, '%s/%s' % (mockTempDir, getTgtPath(tgtPath, srcPath)))

Gateway = SSHBridgeMocker() #DevComment: #Note: Uncomment this line to use the local gateway scripts, instead of the remote ones, so to aid development.
