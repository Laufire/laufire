from ec.types import basics, num
from laufire.ecstore import root, var

@root(filePath='data/store.db')
class Store:

	debug = var(type=basics.yn)

	logLevel = var(type=num.between(1, 5))
