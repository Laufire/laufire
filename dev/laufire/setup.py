r"""
A module that holds setup related data.
"""

Defaults = {

	'projectName': '<unnamed>',

	'delay': 2.0, # The standard wait time.

	'devMode': False,

	'logLevel': 2,

	'fsRoot': '.' # # Risky filesystem operations such as removePath are limited to fsRoot, which defaults to the CWD. For a tighter control, set this var to an absolute path.
}
