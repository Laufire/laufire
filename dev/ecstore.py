r"""A module to help with stroring validated data.

#Later: Branch level hooks that are to be called when any of its Children are changed.
"""
import re

from os.path import exists

from json import loads, dumps
from collections import OrderedDict

from ec.utils import get
from laufire.sqlitex import SQLiteDB, SQLiteSimpleTable
from laufire.extensions import combine
from laufire.parser import parse as _parse

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

		AttrDict[getattr(Child, 'im_func', Child)] = attr # #Note: Functions defined within the classes of the branches are altered as methods. Hence im_func is checked for, to find the original child.

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

def getRoute(branch, path):
	return ('%s/%s' % (branch, path)) if branch else path

def getDataMembers(Dict, branch, Buffer):
	Members = Buffer['Members']
	Order = []
	Members[branch] = {'Order': Order}

	for key, value in Dict.iteritems():
		route = getRoute(branch, key)

		if  hasattr(value, 'iteritems'):
			getDataMembers(value, route, Buffer)

		else:
			Order.append(route)
			Buffer['Values'][route] = value

def processCollected(Dict, branch, Buffer):
	for key, Value in Dict.iteritems():
		Children = Value.get('Children', None)

		route = getRoute(branch, key)

		if Children is not None: # We've got a branch.
			Config = Value['Config']
			Buffer['Members'][route] = Config
			Config['Order'] = [getRoute(route, k) for k in Children]
			processCollected(Children, route, Buffer)

		elif 'Data' in Value: # We've got a data dictionary.
			getDataMembers(Value['Data'], route, Buffer)

		else: # We've got a var.
			Buffer['Members'][route] = Value

def getStoreTable(Config):
	filePath = Config['filePath']
	tableName = Config.get('tableName', 'ecstore')

	DB = SQLiteDB(filePath)
	DB.execute("CREATE TABLE IF NOT EXISTS %s (`route` TEXT PRIMARY KEY, value TEXT)" % tableName)
	DB.close()

	return SQLiteSimpleTable(filePath, tableName, 'route')

def split(route):
	i = route.rfind('/')
	return route[:i] if i > 0 else '', route[i + 1:]

def getBranch(route):
	i = route.rfind('/')
	return route[:i] if i > 0 else ''

def getLeaf(route):
	return route[route.rfind('/') + 1:]

def processCommand(Store):
	import sys
	Argv = sys.argv[1:]

	if not Argv:
		command = 'setup'

	else:
		command = Argv.pop(0)

		if command not in ['setup', 'var', 'dump']:
			raise Exception('Command "%s" is not recognized.' % command)

	ret = getattr(Store, command)(*Argv)

	if ret is not None:
		print ret

# Classes
class ReadOnlyStore:
	def __init__(self, **Config):
		r"""
		Reads the values from the given Store.

		Config:
			filePath: The path to the store.
			tableName (str): The table name of the store, defaults to ecstore.
		"""
		Store = SQLiteSimpleTable(Config['filePath'], Config.get('tableName', 'ecstore'), 'route')
		self._Values = Values = {k: loads(v) for k, v in Store.getCol('value').iteritems()}
		Store.close()

		Routes = Values.keys()
		Routes.sort(lambda x, y: cmp(len(x), len(y)) * -1) # Sort the Routes, descending by length, so that chidren would be processed before parents, thus speeding up the process.

		# Add branch members.
		while Routes:
			currentRoute = Routes.pop(0)
			branch, leaf = split(currentRoute)

			if not leaf or Values.get(branch):
				continue

			Values[branch] = {'Routes': [route for route in Routes if getBranch(route) == branch] + [currentRoute]}
			Routes.append(branch)

	def __getitem__(self, route):
		return self.var(route)

	def var(self, route):
		Value = self._Values[route]

		if Value and 'Routes' in Value: # Return the values from the Children
			Ret = {}

			for i in Value['Routes']:
				Ret[getLeaf(i)] = self.var(i)

			return Ret

		return self._Values[route]

class ConfiguredStore:
	def __init__(self, Buffer, Config):
		self._Members = Members = Buffer['Members']
		self._Values = Values = Buffer['Values']
		self._Store = Store = getStoreTable(Config)

		StoreValues = Store.getCol('value')

		for route, value in Values.iteritems(): # Write any parsed values to the DB, so that the DB could be shared without the parse source.
			self._set(route, value)

		for route, value in StoreValues.iteritems():
			if route in Members:
				Values[route] = loads(value)

			else:
				Store.delete(route)

		for key, value in Values.iteritems():
			Member = Members[key]

			if 'live' in Member:
				Member['hook'](value, 'init')

	def __del__(self):
		if hasattr(self, '_Store'):
			self.close()

	def var(self, route, value=None): #pylint: disable=W0221
		Member = self._Members.get(route)

		if value is None:

			if Member and 'Order' in Member: # Return the values from the Children.
				Ret = {}
				for i in Member['Order']:
					Ret[getLeaf(i)] = self.var(i)

				return Ret

			elif Member.get('live'):
				storeValue = self._Values[route]

				ret = Member['hook'](storeValue, 'get')

				return storeValue if ret is None else ret

			return self._Values[route]

		elif not 'name' in Member: # We've got an updatable node.
			raise Exception('Cannot set the value of parsed data.')

		if 'type' in Member:
			value = Member['type'](value)

		if 'hook' in Member:
			ret = Member['hook'](value) if not Member.get('live') else Member['hook'](value, 'set')

			if ret is not None: # Hooks can manipulate the passed values and return them to be stored.
				value = ret

		self._set(route, value)

	def __getitem__(self, route):
		return self.var(route)

	def setup(self, overwrite=False):
		for route in self._Members['']['Order']:
			if overwrite or route not in self._Values:
				self.get(route, overwrite)

			else:
				print '%s: %s' % (route, self._Values[route])

	def get(self, route, overwrite=False):
		Member = self._Members[route]
		Order = Member.get('Order')
		prefix = '  ' * route.count('/')

		if Order:
			name = Member.get('name')

			if name: #  # We've got a branch
				print '\n%s%s:' % (prefix, name) # #Note" Tabs aren't used for branch identification, due the space constrains of the terminal.

				for route in Order:
					self.get(route, overwrite)

				print ''

			# We've got a parsed. Hence return without doing anything.

		else:
			Values = self._Values

			if route not in Values:
				self._get(route, combine(Member, {'prefix': prefix}))

			elif overwrite:
				self._get(route, combine(Member, {'default': Values[route], 'prefix': prefix})) # Have the existing value as the default.

			else:
				print '%s%s: %s' % (prefix, getLeaf(route), Values[route])

	def _get(self, route, Config):
		self._set(route, get(**Config)) # Get the input from the user and write it to the DB.

	def _set(self, route, value):
		self._Store.set({'route': route, 'value': dumps(value)}) # Set the value in the DB.
		self._Values[route] = value # Set the value in the Cache.

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
		filePath (str): The path to the store.
		tableName (str): The table name of the store, defaults to ecstore.
	"""
	return ReadOnlyStore(**Config)

## Config Decorators
def root(Cls=None, **Config):
	r"""
	Returns a Store for the branches and vars under the decorated class.

	Config:
		filePath: The path to the store.
		tableName (str): The table name of the store, defaults to ecstore.
		noAutoSetup (bool): Skips the auto-setup (setting up the data, when the script is inovked directly).
	"""
	if not Cls: # The decorator has some config. Hence return a wrapper to process the following class.
		return lambda Cls: root(Cls, **Config)

	Collected = collectChildren(Cls)
	Members = {}
	Buffer = {'Members': Members, 'Values': {}}

	processCollected(Collected, '', Buffer)
	Members[''] = {'Order': Collected.keys()} # Add the root member.

	Store = ConfiguredStore(Buffer, Config)

	if not Config.get('noAutoSetup') and Cls.__module__ == '__main__': # Setup the store when the Config script is started as the main script.
		processCommand(Store)

	return Store

def branch(Obj, **Config):
	r"""Decorates the Classes that holds other branches and vars.
	"""
	State.append((getName(Obj, Config), {'Children': collectChildren(Obj), 'Config': Config}, None,))

def var(hook=None, **Config):
	r"""A decorator / function for declaring vars.
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

## Config Functions
def parse(filePath, format=None):
	r"""Adds parsed data to the Store.

	Args:
		Check parser.parse.

	#Note: Parsed data can't be written back ans won't be available on the dumps. The idea behind the function is to making data access easier, by unifiying the configuration.
	"""
	if not exists(filePath):
		raise Exception('No such file: %s' % filePath)

	Parsed = _parse(filePath, format)
	ret = lambda x: x # #Note: The lambda serves as an object marker for the assigned value, during child collection.

	State.append((None, {'Data': Parsed}, ret,))

	return ret

def data(Dict):
	r"""Adds the given dictionary into the store.
	"""
	ret = lambda x: x

	State.append((None, {'Data': Dict}, ret,))

	return ret

def store(**Config):
	r"""Adds the data from the given store to the store, in read-only mode.

	Args:
		Check *getStore*.
	"""
	return data(getStore(**Config)[''])
