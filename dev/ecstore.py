r"""A module to help with stroring validated data.

#Later: Branch level hooks that are to be called when any of its Children are changed.
"""
import re

from json import loads, dumps
from collections import OrderedDict

from ec.utils import get
from laufire.sqlitex import SQLiteDB, SQLiteSimpleTable
from laufire.extensions import resolveRoute, combine

# State
State = []
keyPartPattern = re.compile(r'([^/]+/)')

# Helpers
def getName(Obj, Dict):
	if not 'name' in Dict:
		Dict['name'] = Obj.__name__

	return Dict['name']

def collectChildren(Obj):
	AttrDict = {} # Used to get the name of vars, without hooks.

	for attr in [attr for attr in dir(Obj) if attr[0] != '_']:
		Child = getattr(Obj, attr)

		AttrDict[getattr(Child, 'im_func', Child)] = attr

	childCount = len([attr for attr in dir(Obj) if attr[0] != '_'])
	Children = []

	while childCount:
		childCount -= 1

		childName, Config, Child = State.pop()

		if childName is None:
			childName = AttrDict[Child]

		if not 'name' in Config:
			Config['name'] = childName

		Children.insert(0, (childName, Config,))

	return OrderedDict(Children)

def flatten(Dict, prefix, Buffer):
	for key, Value in Dict.iteritems():
		Children = Value.get('Children', None)

		route = prefix + key

		if Children is not None:
			Config = Value['Config']
			Buffer[route] = Config
			Config['Order'] = ['%s/%s' % (route, key) for key in Children]
			flatten(Children, route + '/', Buffer)

		else:
			Buffer[route] = Value

def getStoreTable(Config):
	filePath = Config['filePath']
	tableName = Config.get('tableName', 'ecstore')

	DB = SQLiteDB(filePath)
	DB.execute("CREATE TABLE IF NOT EXISTS %s (`key` TEXT PRIMARY KEY, value TEXT)" % tableName)
	DB.close()

	return SQLiteSimpleTable(filePath, tableName, 'key')

def split(route):
	i = route.rfind('/')
	return route[:i] if i > 0 else '', route[i + 1:]

def getLeaf(route):
	return route[route.rfind('/') + 1:]

# Classes
class ROStore:
	def __init__(self, **Config):
		r"""
		Reads the values from the given Store.

		Config:
			filePath: The path to the store.
			tableName (str): The table name of the store, defaults to ecstore.
		"""
		Store = SQLiteSimpleTable(Config['filePath'], Config.get('tableName', 'ecstore'), 'key')
		StoreValues = Store.getCol('value')
		Store.close()

		self._Values = Values = {}

		 # Create the nested structure
		Routes = list(set([key[0:key.find('/')] for key in StoreValues.keys() if '/' in key])) # Get the routes to branches.
		Routes.sort(key=len) # Sort the keys by length, so that children won't be processed before parents.

		for route in Routes:
			branch, leaf = split(route)
			resolveRoute(Values, branch, '/')[leaf] = {}

		# Add the values
		for route, value in StoreValues.iteritems():
			branch, leaf = split(route)
			resolveRoute(Values, branch, '/')[leaf] = loads(value)

	def __getitem__(self, key):
		return self.var(key)

	def var(self, route):
		return resolveRoute(self._Values, route, '/')

class Store:
	def __init__(self, Members, Order, Config):
		self._Members = Members
		Members[''] = {'Order': Order} # Add the root member.

		self._Store = Store = getStoreTable(Config)

		self._Values = Values = {}
		
		for key, value in Store.getCol('value').iteritems():
			if key in Members:
				Values[key] = loads(value)

			else:
				Store.delete(key)

	def __del__(self):
		self.close()

	def var(self, route, value=None): #pylint: disable=W0221
		Member = self._Members[route]

		if value is None:

			if 'Order' in Member: # Return the values from the Children
				Ret = {}
				for i in Member['Order']:
					Ret[getLeaf(i)] = self.var(i)

				return Ret

			return self._Values[route]

		if 'type' in Member:
			value = Member['type'](value)

		if 'hook' in Member:
			ret = Member['hook'](value)
			if ret is not None: # Hooks can manipulate the passed values and return them to be stored.
				value = ret

		self._Store.set({'key': route, 'value': dumps(value)}) # Set the value in the DB.
		self._Values[route] = value # Set the value in the Cache.

	def setup(self, overwrite=False):
		for route in self._Members['']['Order']:
			if overwrite or route not in self._Values:
				self.get(route, overwrite)

			else:
				print '%s: %s' % (route, self._Values[route])

	def get(self, route, overwrite=False):
		Member = self._Members[route]
		Order = Member.get('Order')

		if Order is not None:
			print '\n%s:' % Member['name'] # #Note" Tabs aren't used for branch identification, due the space constrains of the terminal.
			for route in Order:
				self.get(route, overwrite)

			print ''

		else:
			if route not in self._Values:
				self._get(route, combine(Member, {'prefix': '  ' * route.count('/')}))

			elif overwrite:
				self._get(route, combine(Member, {'default': self._Values[route], 'prefix': '  ' * route.count('/')})) # Have the existing value as the default.

			else:
				print '%s: %s' % (getLeaf(route), self._Values[route])

	def _get(self, route, Config):
		got = dumps(get(**Config))
		self._Values[route] = got
		return self._Store.set({'key': route, 'value': got})

	def dump(self, route=''):
		Order = self._Members[route]['Order']

		for route in Order:
			Member = self._Members[route]
			if 'Order' in Member:
				print '\n%s:' % re.sub(keyPartPattern, '  ', route)
				self.dump(route)
				print ''

			else:
				print '%s: %s' % (re.sub(keyPartPattern, '  ', route), self._Values.get(route))

	def close(self):
		self._Store.close()

	def reopen(self):
		self._Store.reopen()

# Exports

## Functions
def getStore(**Config):
	r"""
	Returns a shared (read-only) Store.

	Config:
		filePath: The path to the store.
		tableName (str): The table name of the store, defaults to ecstore.
	"""
	return ROStore(**Config)

## Decorators
def root(Cls=None, **Config):
	r"""
	Returns a Store for the branches and vars under the decorated class.

	Config:
		filePath: The path to the store.
		tableName (str): The table name of the store, defaults to ecstore.
	"""
	if not Cls: # The decorator has some config. Hence return a wrapper to process the following class.
		return lambda Cls: root(Cls, **Config)

	Collected = collectChildren(Cls)
	Buffer = {}

	flatten(Collected, '', Buffer)

	return Store(Buffer, Collected.keys(), Config)

def branch(Obj, **Config):
	r"""Decorates the Classes that holds other branches and vars.
	"""
	State.append((getName(Obj, Config), {'Children': collectChildren(Obj), 'Config': Config}, None,))

def var(hook=None, **Config):
	r"""A decorator / function for declarinf vars.
	Properties are declared using var as a function.
	Properties with hooks are defined with using this function as a decorator.

	Config is as same as ec's ArgConfig.
	"""
	if hook:
		Config['hook'] = hook
		name = getName(hook, Config)
		ret = hook

	else: # We've got a simple value or a decorator for hook.
		name = Config.get('name', None)
		ret = lambda hook, **dummy: var(hook, **State.pop()[1]) # If the lambda is called, then it would be by the passing of the hook.

	State.append((name, Config, ret,))
	return ret
