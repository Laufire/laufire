r"""Utilities
"""
import hashlib

from laufire.extensions import namespace

def getMD5(filePath): # #From: http://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
	hashMD5 = hashlib.md5()

	with open(filePath, 'rb') as file:
		for chunk in iter(lambda: file.read(4096), b''): # Read the file as small chunks to avoid buffer overruns.
			hashMD5.update(chunk)

	return hashMD5.hexdigest()

@namespace
def getTimeString():
	import time

	def worker(useLocal=False):
		r"""Returns the current time as a path friendly string.
		"""
		return time.strftime('%y%m%d%H%M%S', (time.localtime if useLocal else time.gmtime)(time.time()))

	return worker
