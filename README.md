KDE KWallet Helpers
===================

This package provides three programs: kwlimport, kwlexport, and kwlmerge
which can be used with the KDE KWallet system.

Requirements
------------

* python >= 2.7 < 3.0
* python-dbus >= 1.1
* python-qt4 (kwlimport w/ -C merge only)

Setup
-----

Run 'make' to generate ui_*.py files.

kwlexport
---------

kwlexport [-o outfile] [-w walletname]

Uses DBus to read the contents of the specified wallet
and writes it to the specified file, or standard out.

```shell
$ kwlexport -w mysecrets | gpg -c -o mysecrets.xml.gpg
```

kwlimport
--------

```shell
kwlimport [-i infile] [-w walletname] [-C ignore|replace|merge]
```

Read the specified file, or standard in and
write the contents to the specified file.
The '-C' ('--conflict=') option select the conflict
resolution strategy.
Currently support are 'ignore' which doesn't change existing entries,
'replace' which always overwrites, and 'merge' which attempts an interactive
merge.

```shell
$ cat mysecrets.xml.gpg | gpg -d | kwlimport -w mysecrets

```

XML File Format
---------------

The XML files used by the kwl* scripts
is copied from that produced by kwalletmanager,
and should be compatible.
