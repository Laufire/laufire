r"""A module to help with stroring validated data.
"""
import re
import json

from collections import OrderedDict

from ec.utils import get
from laufire.sqlitex import SQLiteDB, SQLiteSimpleTable

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

def getStore(Config):
	filePath = Config['filePath']
	tableName = Config['tableName']

	DB = SQLiteDB(Config['filePath'])
	DB.execute("CREATE TABLE IF NOT EXISTS %s (`key` TEXT PRIMARY KEY, value TEXT)" % tableName)
	DB.close()

	return SQLiteSimpleTable(filePath, tableName, 'key')

def getLeaf(route):
	return route[route.rfind('/') + 1:]

# Classes
class Store:
	def __init__(self, Members, Order, Config):
		self._Members = Members
		self._Order = Order

		if not 'tableName' in Config:
			Config['tableName'] = 'ecstore'

		self._Store = Store = getStore(Config)

		self._Values = Values = {}
		loads = json.loads

		for key, value in Store.getCol('value').iteritems():
			if key in Members:
				Values[key] = loads(value)

			else:
				Store.delete(key) # Remove from the DB, the keys, which are not in the Config.

	def var(self, route, value=None):
		Member = self._Members[route]

		if value is None:
			if 'Order' in Member:
				Ret = {}
				for i in Member['Order']:
					Ret[i] = self.var(i)

				return Ret

			return self._Values.get(route)

		if 'type' in Member:
			value = Member['type'](value)

		if 'hook' in Member:
			ret = Member['hook'](value)
			if ret is not None: # Hooks can manipulate the passed values and return them to be stored.
				value = ret

		self._Store.set({'key': route, 'value': json.dumps(value)})
		self._Values[route] = value

	def setup(self, overwrite=False):
		for key in self._Order:
			if overwrite or key not in self._Values:
				self.get(key, overwrite)

			else:
				print '%s: %s' % (key, self._Values[key])

	def get(self, route, overwrite=False):
		Member = self._Members[route]
		Order = Member.get('Order')

		if Order is not None:
			print '\n%s:' % Member['name']
			for key in Order:
				self.get(key, overwrite)

		else:
			if overwrite or route not in self._Values:
				self._Store.set({'key': route, 'value': json.dumps(get(**Member))})

			else:
				print '%s: %s' % (getLeaf(route), self._Values[route])

	def dump(self, Member=None):
		Order = Member['Order'] if Member else self._Order

		for key in Order:
			Member = self._Members[key]
			if 'Order' in Member:
				print '\n%s:' % re.sub(keyPartPattern, '\t', key)
				self.dump(Member)

			else:
				print '%s: %s' % (re.sub(keyPartPattern, '\t', key), self._Values.get(key))

# Decorators
def root(Cls=None, **Config):
	if not Cls: # The decorator has some config.
		return lambda Cls: root(Cls, **Config)

	Collected = collectChildren(Cls)
	Buffer = {}

	flatten(Collected, '', Buffer)

	return Store(Buffer, Collected.keys(), Config)

def var(hook=None, **Config):
	if hook:
		Config['hook'] = hook
		name = getName(hook, Config)
		ret = hook

	else: # We've got a simple value or a decorator for hook.
		name = Config.get('name', None)
		ret = lambda hook, **dummy: var(hook, **State.pop()[1]) # If the lambda is called, then it would be by the passing of the hook.

	State.append((name, Config, ret,))
	return ret

def branch(Obj, **Config):
	State.append((getName(Obj, Config), {'Children': collectChildren(Obj), 'Config': Config}, None,))
