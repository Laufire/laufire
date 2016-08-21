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

* Try the package on linux.

Pending
-------

* Make the package publishable.

* Bring the venv management too. It's not yet brought in due to it being costly and due to not many projects needing it.

Later
-----

* Measure the speed of the package and improve if necessary.

* Add tests.

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
	* 1920	Improved ecstore to be a replacement for the existing settings management.

* 160816

	* 0122	Added initializer.
	* 1655	Introduced laufire.mock, a package to help with mocking, so to ease development.
	* 1655	Extracted ssh.SSHBridgeMocker as a separate package, mock.ssh.
	* 1930	Added setup.py.
	* 2040	Tuned the modules to be more sharable.
	* 2150	Added Project.devMode, which prepares the project for development, by adding a few functions from laufire.dev, as built-ins.

* 160817

	* 0100	Improved laufire.ssh.
	* 1915	Extracted the package as a separate repo.
	* 2020	Restructured the dirs for further development.
	* 2346	Finished the project structure.
	* 2346	First deployment.

* 160818

	* 0243	ecstore's Stores can now be accessed like dictionaries.
	* 0630	Introduced ecstore.getStore, to have read-only stores, that can be shared across projects.
	* 2000	Added laufire.parser.
	* 2010	Introduced ecstore.parse, to have parsed data from JSON and YAML files.
	* 2130	Write-proofed ecstore. The *var* methods of various Classes, always return a copy of the underlying data.
	* 2310	Rewrote ecstore.ROStore.__init__, to be more readable.
	* 2340	Data from ecstore.parse are now written to the DB, so that the DB-s could be shared with other projects.

* 160819

	* 0415	Added ecstore.data, to help with managing dictionaries from other sources.
	* 0430	Added ecstore.store.

* 160820

	* 0600	Added helpers.filesys to make filesys cross-platform.
	* 1830	Config files for ecstore are now directly callable. The call initiates the set of the configured store.
	* 2055	Fixed a bug in sqlitex: There was some infinite recursion, during the GC of SQLiteDB-s which had their initialization failed.


* 160821

	* 1030	Project.ConfigExtensions can now be nested dictionaries, they are merged with that of Config.

* 160822

	* 1000	Most modules doesn't import Project anymore, so now these modules can now be used without defining a Project.
	* 1030	ecstore.var now supports: get, set and init through hooks.
	* 1052	Store scripts could now be called, directly with ec syntax, to perform setup etc. Currently the commands setup, var and dump are supported.
