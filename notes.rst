laufire
=======

	A set of modules to help with ops.

Idea
----

* The idea is to have a sharable utility module, across projects to save on development and debugging time.

Modules
-------

* **extensions.py** - provides generic low level functions to assist development.

* **filesys.py** - helps with handling the filesystem tasks.

* **logger.py** - meant to be the provider of logging functionality.

* **shell.py** - helps with dispatching commands through the shell.

* **sqlitex.py** - a simple wrapper over the native sqlite3 library.

* **yamlex.py** - helps with handling yaml-s.

* **ecstore** - provide persistent storage facilities.

Caveats
-------

* In Windows, some functionality requires admin priviliges.

ToDo
----

* Update the dependencies.

* Make the package OS independent.

	* **shell.run(..., shell=True)** doesn't run as expected on macs.

* Replace YamlEx with a generic dictionary (ordered) dictionary templater, so to allow using other data formats for interpolation.

* Update the Modules section.

Pending
-------

* Redo the debug logs.

* Add a requirements file.

* Fix filesys.collectPaths. It has a lot of differences from the existing glob libraries.

* Setting 'logLevel' through ecstore init hooks, isn't working if the underlying logger was loaded by some other module, before initialization (this loggerd will have the default name <unnamed*).

* Ensure that ecstores opened with *getStore* couldn't be corrupted, accidentally while importing.

* Restructure the Config format, especially for the settings keys like **Paths** (for Gateway Config) etc.

* Add a module for cryptography, especially to help with storing sensitive data on ecstore. Live hooks could be used to encrypt and decrypt the values.

* Write tests.

* Make the package publishable.

* Bring the venv management too. It's not yet brought in due to it being costly and due to not many projects needing it.

Later
-----

* Think of maintaining a package repo. It seems like easy_install can use simple file servers as repos. Hence, no PyPI server would be required.

* Measure the speed of the package and improve if necessary.

* Complete the test suite.

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

* 161227

	* 1600	Added dev.plot.

* 170105

	* 2321	Added an argument, createMissingFile to tsv.TSV's constructor.

* 170110

	* 0232	Added filesys.getLines.

* 170217

	* 1533	Added YamlEx.extend.

* 170315

	* 0741	Rewrote the module crypto to use **pyaes**, instead of **pycrypto**, which required GCC for installing.

* 170418

	* 1750	Added filesys.rename.

* 170420

	* 1917	Added filesys.iterateContent.
	* 1958	Added utils.getMD5ForIterable.

* 170421

	* 0232	Introduced a new module, decorators, to help with decorating functions.

* 170422

	* 1733	Bug Fixed: In decorators.memoize, caching sometimes failed due to the discrepancies with JSON decoding during the hash generation.

* 170423

	* 0059	Added decorators.rerun,

* 170529

	* 2149	The command ecstore.var now accepts inputs to the vars through stdin.

* 170712

	* 0023	Added sqliteex.execute, a quick call to execute queries on DBs.

* 170713

	* 0247	Added the option filesys.backup.keepOriginal, to make a copy of the source file, instead of moving it during the process.
	* 1637	Added extensions.unpack.

* 170714

	* 1439	Bug Fixed: filesys.resolve was buggy.
	* 2104	flow.waitFor now returns the value of the waiting function.
	* 2230	Added dev.hl (highlight), a colored variation of peek.

* 170720

	* 1825	Bug Fixed: flow.interactive.message wasn't optional.

* 170721

	* 0410	Imported prepro.helpers.linkTree as filesys.linkTree.
	* 0410	Introduced debug logging to some key filesys calls.
	* 0429	Introduced logger.dump.
	* 0432	Reduced the output from the module shell.

* 170722

	* 0012	Introduced shell.writable, as a way to write to the STDIN of the spawned process.

* 170725

	* 0340	Introduced filesys.isLocked.

* 170726

	* 0444	Introduced tools, a set of modules to aid with well defined problems.
	* 0444	Introduced tools.ss.
	* 0558	Introduced the argument, dev.interactive.raiseError, which when true, raised any errors instead of returning it.
	* 2222	Inreoduce dev.tee.

* 170728

	* 0816	Bug fixed: filesys.linkTree wans't making parent dirs, but linked them, when hardLinks was set to true.

* 170730

	* 2245	Bug fixed: flow.retry slept an extra time, after the call returned success.
	* 2315	Introduced tools.retry.

* 170731

	* 0724	mock.ssh.callScript now raises an exception with the got stdout as its message, if the out weren't JSON
	* 0826	Introduced filesys.pair.

* 170803

	* 1256	mock.ssh now resembles ssh, a bit more closely.
	* 1414	Fixed a lot of bugs in filesys. Linking and path removal were buggy.

* 170804

	* 0219	filesys dosen't depend on the package, glob2 anymore.
	* 0311	filesys dosen't depend on the package, shutil anymore.
	* 0759	filesys.linkTree and now uses Includes and Excludes, rather than globs.
	* 0759	Removed the option filesys.collectPaths.absPaths.
	* 0930	filesys.getPathPairs now use Includes, instead of globs.

* 170805

	* 1329	Bug fixed: symlinks weren't working, due to	incompatible path separators.
	* 1351	filesys.linkTree.hardLinks now defaults to true, as WAMP doesn't handle symlinks well.

* 170810

	* 1932	Added filesys.appendContent.
	* 1945	Improved the handling of path separators.
	* 1948	Added filesys.getAncestor.

* 170816

	* 1705	SSH now uses *$HOME* instead of *~*, as the former has better support in bash.

* 170817

	* 1858	ssh and its mock do not support path expansions anymore, in order to make the structure robist and flexible.

* 170823

	* 1420	Introduced initializer.stealCWD.
	* 2216	SSHBridge.GatewayConfig is now SSHBridge.Config, so is that of SSHBridgeMocker.

* 170824

	* 1524	SSHBridge.upload now supports templatable values.
	* 1524	Uploads are now retried.

* 170825

	* 2300	Decided to standardize the path separator as '/', disregarding the OS. Dicrepancies will be managed internaly.

* 170827

	* 0140	Introduced filesys.joinPaths.
	* 0220	Simplified the globs used in the module filesys.
	* 0220	Rewrote filesys.collectPaths.
	* 0243	Dumped filesys.expandGlobs, to avoid having two glob standards within the same module.
	* 2200	Decided to choose file safety over performance. Thus, every remove and write call would ensure the safety of the target before proceeding. It would be applied through an option named *autoClean* with every such function.

* 170828

	* 0325	Restructured the module filesys to be more simple and safe.
	* 0325	Many functions of the module, filesys got a new argument *autoClean*, which defaults to true and eases file-modifications within the fsRoot and makes the modifications out of it tougher.
	* 0325	Renamed the filesys option *hardLinks* to *hardLink*, as a verb.
	* 0325	Reordered and categorized the functions of the module, filesys.
	* 0325	Introduced filesys.requireAncestor, makeDir and stdPath.
	* 0355	filesys.copy now support patterns.

* 170829

	* 0213	Bug fixed: filesys.copy and linkTree failed with recursive file patterns.
	* 0334	Added a missing option, filesys.copyContent.autoClean.

* 170829

	* 1617	Fixed several bugs in the module, filesys.
	* 1740	Linted the scripts.

* 170830

	* 1607	Introduced filesys.glob, a simpler wrapper around filesys.collectPaths.

* 171209

	* 0536	Wrote a preliminary setup file.
	* 0659	Made the module deployable.
	* 0701	Released v0.0.1.

* 180221

	* 0602	Introduced a Windows specific requirements file.
	* 0607	Open-sourced the project with MIT license.

* 180227

	* 1925	Bug fixed: The nix implementation of some FileSys calls were buggy.

* 181019

	* 1845	Bug fixed: The package dependencies weren't listed properly.

* 181120

	* 2045	Fixed a bug in the nix implementation of filesys.collectPaths.
 
 * 181126

	* 1349	Made the requirements file platform independent.
	