r"""
A simple tool to help with re-running failed tasks.

#Note: This module could be called from the command line.
#Usage: python -m laufire.retry "command" <cwd> <repeats> <delay>
"""
# Exports
def retryCommand(command, repeat, delay, **KWArgs):
	r"""
	The keyword arguments are for shell.run.
	"""
	from laufire.flow import retry
	from laufire.shell import run
	from time import time

	State = {'tries': 0, 'exitCode': None}

	def worker():
		exitCode = run(command, **KWArgs)

		State['tries'] += 1
		State['exitCode'] = exitCode

		if not exitCode:
			return 1

	start = time()

	retry(worker, repeat, delay)

	return State['exitCode'], State['tries'], time() - start

# Main
def main():
	import sys
	from laufire.logger import log

	Args = sys.argv[1:]
	command = Args[0]
	cwd = Args[1] if len(Args) > 1 else '.'
	repeat = int(Args[2]) if len(Args) > 2 else 1
	delay = int(Args[3]) if len(Args) > 3 else 0

	exitCode, tries, duration = retryCommand(command, repeat, delay, cwd=cwd)

	log('tries: %s' % tries, 'LIGHTGREEN_EX')
	log('duration: %s' % duration, 'LIGHTYELLOW_EX')

	sys.exit(exitCode)

if __name__ == '__main__':
	main()
