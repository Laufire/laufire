laufire
=======

	A set of modules to help with ops.

Idea
----

* The idea is to have a sharable, utility module across the projects to save on development and debugging time.

Modules
-------

* **extensions.py** - provides generic low level functions to assist development.

* **filesys.py** - helps with handling the filesystem tasks.

* **logger.py** - meant to be the provider of logging functionality.

* **shell.py** - helps with dispatching commands through the shell.

* **sqlitex.py** - a simple wrapper over the native sqlite3 library.

* **yamlex.py** - helps with handling yaml-s.

* **ecstore** - provide persistent storage facilities.

ToDo
----

* **None, yet.**

Pending
-------

* Make the package publishable.
* Bring the venv management too.

Log
---

* 160813

	* 1800	Added the module logger.
	* 1800	Introduced two new modules, dev and flow.
	* 2310	Added all the standalone modules.

* 160814

	* 0600	Added more calls and restructured several modules.

* 160815

	* 1040	Added ecstore.
	* 1800	Added a few methods to sqlitex.SQLiteSimpleTable, so to be used by ecstore.
	* 1920	Improved ecstore to be a replacement for the existing setting management.

* 160816

	* 0122	Added initializer.
	* 1655	Introduced laufire.mock, a package to help with mocking, so to ease development.
	* 1655	Extracted ssh.SSHBridgeMocker as a separate package, mock.ssh.
