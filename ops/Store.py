from ec.types import multi
from laufire.ecstore import root, var

@root(filePath='data/store.db')
class Store:
	TargetParents = var(type=multi.multi(';', type_str='a list of paths separated by semi-colons'))
