r"""
A module to help with debelopment.
"""
import json

from laufire.filesys import copy, ensureParent
from laufire.logger import debug
from laufire.shell import call, debugCall, assertShell
from laufire.ssh import GatewayConfig, getTgtPath

MockConfig = GatewayConfig['Mock']
mockTempDir = MockConfig['tempDir']
mockScriptTpl = MockConfig['scriptTemplate']
scriptsDir = MockConfig['scriptsDir']

class SSHBridgeMocker:
	r"""A class to help with the development of gateway scripts, by executing the commands locally.
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
		tgtPath = '%s/%s' % (mockTempDir, getTgtPath(tgtPath, srcPath))
		ensureParent(tgtPath)
		return copy(srcPath, tgtPath)

Gateway = SSHBridgeMocker()
