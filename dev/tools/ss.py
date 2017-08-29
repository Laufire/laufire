r"""
SS
==

	A simple shell, that helps to interact with the given function.
"""
def interact(func, prompt='>'):
	r"""
	Interact with the given function. The interaction can be closed by typing the EOF character.
	"""
	while True:
		try:
			func(raw_input(prompt))

		except EOFError:
			break

		except Exception as e: #pylint: disable=broad-except
			print e
