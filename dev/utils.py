r"""Utilities
"""
def getMD5(filePath): # #From: http://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
	r"""Returns the MD5 digest of the given file.
	"""
	import hashlib

	hashMD5 = hashlib.md5()

	with open(filePath, 'rb') as file:
		for chunk in iter(lambda: file.read(4096), b''): # Read the file as small chunks to avoid buffer overruns.
			hashMD5.update(chunk)

	return hashMD5.hexdigest()

def getTimeString(useLocal=False):
	r"""Returns the current time as a path friendly string.
	"""
	from datetime import datetime

	return (datetime.now if useLocal else datetime.utcnow)().strftime('%y%m%d%H%M%S%f')[:-3]

def getRandomString(length=8):
	import random
	import string

	return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

def getFreeName(iterable):
	r"""Gets a free name for the given iterable.
	"""
	while True:
		name = getRandomString()

		if name not in iterable:
			return name
