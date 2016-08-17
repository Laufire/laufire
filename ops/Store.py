from ec.types import multi
from laufire.ecstore import root, var

@root(filePath='data/store.db')
class Store:
	TargetParents = var(type=multi.multi(';'), desc='TargetParents, a list of paths separated by semi-colons', type_str=None) # The targets for deployment, separated by a pipe.
