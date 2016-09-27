r"""
A module to help with changing envirnment settings.
"""
def enableUnicodePrinting():
	r"""
	Enables the printing of unicode characters, bot through stdout and stderr.
	"""
	import codecs
	import sys

	sys.stdout = codecs.getwriter('utf8')(sys.stdout)
	sys.stderr = codecs.getwriter('utf8')(sys.stderr)
