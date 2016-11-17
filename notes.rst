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

* Fix filesys.collectPaths. It has a lot of differences from the existing glob libraries. Also try to yield paths instead of returnig them.

* Setting 'logLevel' through ecstore init hooks, isn't working if the underlying logger was loaded by some other module, before initialization (this loggerd will have the default name <unnamed*).

* Ensure that ecstores opened with *getStore* couldn't be corrupted, accidentally while importing.

* Restructure the Config format, especially for the settings keys like **Paths** (for Gateway Config) etc.

* Add a module for cryptography, especially to help with storing sensitive data on ecstore. Live hooks could be used to encrypt and decrypt the values.

* Write tests.

* Make the package publishable.

* Bring the venv management too. It's not yet brought in due to it being costly and due to not many projects needing it.

Later
-----

* Measure the speed of the package and improve if necessary.

* Add tests.

* Add support for LZMA, without delegating it to binaries.

* Think of adding Project.workDir as the base work path (for file operations etc), which could save the accidental deletion of source files.

Tips
----

* The config files can interpolate values from the Store.

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
	* 1703	Bug fixed: In ecstore, The previous additions didn't integrate with the existing structure.
	* 1926	Bug fixed: In ecstore, nested dictionaries from external sources were not parsed properly.

* 160822

	* 0320	Introduced filesys.compress and filesys.extract.
	* 0525	Bug fixed: In filesys.compress. Path handling had some issues.

* 160825

	* 0625	Changed the yielded values of extensions.walk.

* 160826

	* 0033	Added laufire.mockable as a centralized provider for mockables and their mocked counterparts.
	* 0330	Tuned the module, ecstore.
	* 0630	Added shell.piped.

* 160829

	* 0339	utils.getTimeString made more precise, by adding milli-seconds.
	* 1419	Added sqlitex.SQLiteDB.execFile, to help with executing SQL files.
	* 1506	Added sqlitex.SQLiteDB.importTablesFromFille.

* 160904

	* 0658	Bug Fixed: filesys.isDescendant was considering paths to be the descendants of themselves.
	* 0837	Bug Fixed: filesys.makeLink wasn't working on linux.

* 160906

	* 0714	Robusted the filesys functions copy and makeLink.
	* 1800	Added shell.getProcessData.

* 160917

	* 0016	Bug fixed. In filesys.collectPaths, Dirs weren't excluded based on the exclusion argument.

* 160921

	* 1927	Bug fixed: In filesys.isDescendant.

* 160922

	* 1433	Bug fixed: In filesys.backup. Backups are done to wrong targets if the CWD and the backup path differed.

* 160923

	* 1241	Redid filesys.makeLink, now it supports both hard and soft links, with soft as the default.
	* 1700	Bug fixed: In ecstore.ReadOnlyStore. The processing of the routes was buggy.
	* 1834	Added ecstore.value, to have read-only values.

* 160924

	* 0026	Bug fixed: in filesys.makeLink, the implementation was buggy.
	* 0330	Improved path handling in the module, gitcli.

* 160925

	* 1935	Project files now support two new options, **cwd** and **Paths**.
	* 1950	Tuned the module, YamlEx.

* 160927

	* 2320	Added the module, tools.

* 161011

	* 0820	Bug Fixed: extensions.flatten wasn't behaving as exepected. When resoving, made it support both recrsive and vanila flatten, through an extra argument, recursive.

* 161014

	* 1013	Added osbridge.getOSRoot
	* 1013	Added osbridge.getDataFolder is now, osbridge.getDataDir.

* 161023

	* 1835	Supressed debug messages are now accesbile through logger.Supressed. This is to aid debugging.

* 161025

	* 1027	Added filesys.restore.

* 161105

	* 2324	Added the module crypto, to help with basic string encryption and decryption.

* 161117

	* 0733	Added filesys.ensureDir.
	* 1610	Added extensions.select.
	* 2030	Improved shell.pipe.
	* 2030	Bug fixed: filesys.collectPaths wasn't traversing symlinks on Linux.
