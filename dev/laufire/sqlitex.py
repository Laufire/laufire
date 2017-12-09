import sqlite3

# #Pending: Raise exceptions on constraint failures etc.

# Helpers
def dictFactory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]

	return d

# Exports
def execute(filePath, query, useDict=False):
	r"""Executes the given query over the given DB and returns the results, if any.
	"""
	DB = SQLiteDB(filePath, useDict)
	return DB.execute(query).fetchall()

class SQLiteDB:
	def __init__(self, filePath=':memory:', useDict=False):
		r"""
		A simple wrapper over native sqlite3, to ease development.

		Args:
			filePath (str): The path to the sqlite file.
			useDict (bool, Fale): SELECT-s return a list of dictionaries when set to True.

		Note:
			The calss handles a single DB and allows only a single cursor over a single connection.
		"""
		self._inited = False # Used to break getattr chains, that occur on connection opening errors.

		self.path = filePath
		self._conn = sqlite3.connect(self.path)

		if useDict:
			self._conn.row_factory = dictFactory

		self._cur = self._conn.cursor()

		self._inited = True

	def __del__(self):
		if self._inited:
			self.close()

	def execFile(self, filePath):
		r"""Helps with executing sql files.
		"""
		for line in open(filePath):
			self.execute(line.rstrip('\r\n '))

	def close(self):
		r"""Close the DB.

		Any uncommited changes will be commited before closing.
		"""
		if self._conn:
			self._conn.commit()
			self._conn.close()
			self._conn = None

	def reopen(self):
		r"""Reopens a closed DB.
		"""
		self.__init__(self.path)

	def __getattr__(self, attr):
		r"""
		Allows the access of the methods of the underlying cursor / connection.
		"""
		return getattr(self._cur, attr) if hasattr(self._cur, attr) else getattr(self._conn, attr)

class SQLiteSimpleTable(SQLiteDB):
	def __init__(self, filePath=':memory:', tableName='unnamed', key=None):
		r"""
		An extension to the class, SQLiteDB that simplifies the access of tables with a primary key.

		The in and out values are simple dicts, with keys matching the field names of the table.

		#Note: When no key is specified the key is got from the table info.
		"""
		SQLiteDB.__init__(self, filePath, True)
		self.tableName = tableName

		self.execute("PRAGMA table_info(`%s`);" % tableName)

		Record = self.fetchone()

		if not Record:
			raise Exception('No such table %s, in the DB: %s' % (tableName, filePath))

		if not key:
			while Record:
				if Record['pk'] == 1:
					key = Record['name']
					break

				Record = self.fetchone()

		if not key:
			raise Exception('No primary key found for the table %s, in the DB: %s' % (tableName, filePath))

		self._key = key
		self._Statements = {

			'get': "SELECT * FROM `%s` WHERE `%s`=?;" % (tableName, key),
			'getColTpl': "SELECT %s, `%%s` FROM `%s`;" % (key, tableName),
			'getAll': "SELECT * FROM `%s`;" % tableName,
			'del': "DELETE FROM `%s` WHERE `%s`=?;" % (tableName, key),
			'update': "UPDATE OR IGNORE %s SET %%s WHERE `%s`=:%s;" % (tableName, key, key),
			'insert': "INSERT OR IGNORE INTO %s (%%s) VALUES (%%s);" % tableName,
		}

	def get(self, key):
		self.execute(self._Statements['get'], [key])
		return self.fetchone() or {}

	def getCol(self, colName):
		Ret = {}
		keyCol = self._key

		for Item in self.execute(self._Statements['getColTpl'] % colName).fetchall():
			Ret[Item[keyCol]] = Item[colName]

		return Ret

	def getAll(self):
		Ret = {}
		keyCol = self._key

		for Item in self.execute(self._Statements['getAll']).fetchall():
			Ret[Item[keyCol]] = Item

		return Ret

	def set(self, Values, dontInsert=False):
		# #From: http://stackoverflow.com/questions/14108162/python-sqlite3-insert-into-table-valuedictionary-goes-here
		Keys = [key for key in Values.keys() if key != self._key]
		updateStr = ','.join(['`%s`=:%s' % (key, key) for key in Keys])

		Keys = Values.keys()
		columns = '`%s`' % '`,`'.join(Keys)
		placeholders = ':'+',:'.join(Keys)

		self.execute(self._Statements['update'] % updateStr, Values)

		if not dontInsert:
			self.execute(self._Statements['insert'] % (columns, placeholders), Values)

		self.commit()

	def delete(self, key):
		self.execute(self._Statements['del'], [key])
		self.commit()

	def reopen(self):
		self.__init__(self.path, self.tableName, self._key)

def importTables(toDBPath, fromDBPath, TableNames):
	TargetDB = SQLiteDB(toDBPath)
	TargetDB.execute('ATTACH ? as patch', [fromDBPath])

	for tableName in TableNames:
		TargetDB.execute('INSERT OR REPLACE INTO {0} SELECT * FROM patch.{0};'.format(tableName))

	TargetDB.execute('DETACH patch;')
	TargetDB.execute("VACUUM;")
	TargetDB.commit()
	TargetDB.close()

def importTablesFromFile(toDBPath, fromFilePath, tableName=None, delimiter='\t', lineterminator='\n'):
	import csv

	if not tableName:
		from os.path import splitext, basename
		tableName = basename(splitext(fromFilePath)[0]) # Use the file name as the table name.

	Rows = [Row for Row in csv.reader(open(fromFilePath, 'rb+'), delimiter=delimiter, lineterminator=lineterminator)]

	if not Rows:
		return

	TargetDB = SQLiteDB(toDBPath)
	TargetDB.executemany('INSERT OR REPLACE INTO {0} VALUES({1});'.format(tableName, ','.join(['?'] * len(Rows[0]))), Rows)
	TargetDB.execute("VACUUM;")
	TargetDB.commit()
	TargetDB.close()
