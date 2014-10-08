===============
kotti_filestore
===============

Filesystem storage of BLOBs for Kotti_.

`Find out more about BLOB storage in Kotti`_

Setup
=====

To activate the ``kotti_filestore`` add-on in your Kotti site, you need toadd an entry to the ``kotti.configurators`` setting in your Paste Deploy config.
If you don't have a ``kotti.configurators`` option, add one.
The line in your ``[app:main]`` (or ``[app:kotti]``, depending on how you setup Fanstatic) section could then look like this::

    kotti.configurators = kotti_filestore.kotti_configure

You also need an option to tell Kotti to use the ``kotti_filestore`` add-on and to configure the location where the BLOBs will be stored on the filesystem::

  kotti.blobstore = kotti_filestore.filestore://%(here)s/filestore

The ``kotti_filestore.filestore`` part will cause Kotti to delegate the storage of BLOBs to this class.
The ``%(here)s/filestore`` is an example configuration for the storage which will cause all BLOBs to be stored in a directory named ``filestore`` which will be automatically created in the same folder where your config file resides.


.. _Kotti: http://pypi.python.org/pypi/Kotti
.. _Find out more about BLOB storage in Kotti: http://kotti.readthedocs.org/en/latest/developing/blobstorage.html
