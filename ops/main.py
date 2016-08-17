r"""
main
====

	The entry point for Ops.
"""
from Project import Config

from ec.ec import task, arg, group, settings
from ec.types.basics import yn

from laufire.filesys import makeLink
from Store import Store as _Store

@group(alias='s')
class Store:
	@task(alias='s', desc='Setup the store.')
	@arg(alias='r', type=yn, desc='Reconfigure all data. Defaults to no.', default=False)
	def setup(reconfigure):
		_Store.setup(reconfigure)

@task(alias='d', desc='Deploys the package to the targets from the store.')
def deploy():
	libPath = '../dev'

	for targetParent in Config['TargetParents']:
		makeLink(libPath, '%s/laufire' % targetParent)

settings(debug=True)
