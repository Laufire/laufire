r"""
A module with constructors for mockable objects and their mocks.
"""

# State
Gateway = None

def getGateway(Config, shouldMock, cached=True):
	r"""
	Returns a Gateway according to the passed params.

	Args:
		Config (dict): The Config as expected (should have SSH, Gateway and Mock configs).
		shouldMock (bool): Returns the mocker when set to True.
		cached (bool): Shares a cached Gateway instead of creating a new one with every call.
	"""
	if cached:
		global Gateway

		if Gateway:
			return Gateway

	if shouldMock:
		from laufire.mock.ssh import SSHBridgeMocker
		Gateway = SSHBridgeMocker(Config)

	else:
		from laufire.ssh import SSHBridge
		Gateway = SSHBridge(Config)

	return Gateway
