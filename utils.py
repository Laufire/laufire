r"""Utilities
"""
from laufire.extensions import namespace

@namespace
def getMD5(): # #From: http://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
	import hashlib

	def worker(filePath): # #From: http://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
		hashMD5 = hashlib.md5()

		with open(filePath, 'rb') as file:
			for chunk in iter(lambda: file.read(4096), b''): # Read the file as small chunks to avoid buffer overruns.
				hashMD5.update(chunk)

		return hashMD5.hexdigest()

	return worker

@namespace
def getTimeString():
	import time

	def worker(useLocal=False):
		r"""Returns the current time as a path friendly string.
		"""
		return time.strftime('%y%m%d%H%M%S', (time.localtime if useLocal else time.gmtime)(time.time()))

	return worker

@namespace
def getRandomString():
	import random
	import string

	def worker(length=8):
		return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

	return worker

def getFreeName(iterable):
	r"""Gets a free name for the given iterable.
	"""
	while True:
		name = getRandomString()

		if name not in iterable:
			return name
