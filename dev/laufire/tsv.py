r"""A module to help reading and writing TSV (tab separated files).

#Note: TSV is chosen over CSV for their simplicity.
"""
import csv
from os.path import exists

class TSV:
	def __init__(self, filePath=None, mode='dict', createMissingFile=False): # #Note: Mode could be set to 'list' to handle data as list of lists.
		r"""
		A simple class to help with reading and writing TSV files.
		"""
		self._file = None

		if filePath:
			if createMissingFile and not exists(filePath):
				file = open(filePath, 'wb+')
				file.close()

			self.open(filePath, mode)

	def open(self, filePath, mode='dict'):
		r"""Opens the given file.
		"""
		if self._file:
			self.close()

		self._filePath = filePath
		self._file = open(filePath, 'rb+')

		if mode == 'dict':
			self._reader = csv.DictReader(self._file, delimiter='\t', lineterminator='\n')
			self.FieldNames = self._reader.fieldnames
			self._writer = csv.DictWriter(self._file, self.FieldNames, delimiter='\t', lineterminator='\n')

		else:
			self._reader = csv.reader(self._file, delimiter='\t', lineterminator='\n')
			self.FieldNames = None
			self._writer = csv.writer(self._file, delimiter='\t', lineterminator='\n')

	def read(self):
		r"""Returns an iterable reader.
		"""
		return self._reader

	def write(self, *Rows): #Pending: Make the call to utilize iterators.
		r"""Appends the given rows to the file.
		"""
		return self._writer.writerows(Rows)

	def empty(self):
		r"""Clears all the data from the file.
		"""
		self._file.seek(0)
		self._file.truncate()

		if self.FieldNames:
			self._writer.writeheader()

	def close(self):
		r"""Closes the file.
		"""
		self._file.close()
		self._file = None

def readTSV(filePath, mode='dict'):
	r"""Reads and returns every row from the given TSV file.

	Args:
		filePath (str): The path to the TSV file.
		mode (dict/list): Sets the type of the items in the returned list.
	"""
	TsvFile = TSV(filePath, mode)

	Rows = [row for row in TsvFile.read()]

	TsvFile.close()
	return Rows
