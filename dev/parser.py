r"""
parse
=====

A set of functions to parse data files of various data formats.
"""
from os.path import splitext

# Helpers
def getParser(filePath):
	return ParserMap[splitext(filePath)[1][1:].lower()]

# Exports
def parseYAML(filePath):
	from laufire.yamlex import YamlEx

	Data = YamlEx(filePath)
	Data.interpolate()

	return Data

def parseJSON(filePath):
	import json

	with open(filePath, 'r') as file:
		return json.load(file)

def parse(filePath, format=None):
	r"""Parses data from the diven file.

	Args:
		filePath (str): The path to process.
		format (str): The format of the file. When not given, it is detected based on the files extension. For supported formats check the var ParserMap.
	"""
	return (ParserMap[format] if format else getParser(filePath))(filePath)

# Data
ParserMap = {'yml': parseYAML, 'yaml': parseYAML, 'json': parseJSON}
