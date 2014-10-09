===============
kotti_filestore
===============

Filesystem storage of BLOBs for Kotti_.

`Find out more about BLOB storage in Kotti`_

Setup
=====

You only need to add an option to tell Kotti to use the ``kotti_filestore`` add-on and to configure the location where the BLOBs will be stored on the filesystem.
The line in your ``[app:main]`` (or ``[app:kotti]``, depending on how you setup Fanstatic) section could then look like this::

  kotti.blobstore = kotti_filestore.filestore://%(here)s/filestore

The ``kotti_filestore.filestore`` part will cause Kotti to delegate the storage of BLOBs to this class.
The ``%(here)s/filestore`` is an example configuration for the storage which will cause all BLOBs to be stored in a directory named ``filestore`` which will be automatically created in the same directory where your config file resides.

Configuration
=============

Currently a single configuration option exists.
The absolute path of the directory where ``kotti_filestore`` stores the BLOBs can be specified with the path segment of the configuration URL.

To overcome limitations w.r.t. the maximum number of files within a directory on some filesystems, ``kotti_filestore`` generates a directory tree with a depth of 16, where each directory has a maximum of 256 children (either subdirectories or files).

TODO
====

- ``kotti_filestore`` tries to be fully transaction aware.

  It does so by using `repoze.filesafe`_ for filesystem operation on **files**.
  Unfortunately ``repoze.filesafe`` doesn't provide functions for **directories**.
  That's why ``kotti_filestore`` may leave some empty directories on your filesystem.
  Files are removed properly on deletion of the corresponding content items though.

  As a workaround you are encouraged to setup a cronjob that scans for empty directories periodically and removes them.

.. _Kotti: http://pypi.python.org/pypi/Kotti
.. _Find out more about BLOB storage in Kotti: http://kotti.readthedocs.org/en/latest/developing/blobstorage.html
.. _repoze.filesafe: http://docs.repoze.org/filesafe/
