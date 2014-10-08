# -*- coding: utf-8 -*-

"""
Created on 2014-07-26
:author: Andreas Kaiser (disko)
"""

import os
from logging import getLogger
from uuid import uuid4

import transaction
from kotti.interfaces import IBlobStorage
from pyramid.util import DottedNameResolver
from repoze.filesafe import create_file
from repoze.filesafe import delete_file
from repoze.filesafe import open_file
from yurl import URL
from zope.interface import implements


log = getLogger(__name__)


def kotti_configure(settings):
    """ Kotti configuration.  This function is called by Kotti during startup.

    :param settings: Settings from the PasteDeploy ini file.
    :type settings: dict
    """

    # Parse the ``kotti.blobstore`` option as an URL.
    url = URL(settings['kotti.blobstore'])

    # The scheme / protocol part of the URL is the dotted class name of the
    # BlobStorage provider.
    factory = DottedNameResolver(None).resolve(url.scheme)

    # Create an instance of the provider, passing it the path part of the URL
    # as its configuration and store the instance in the settings dict.
    settings['kotti.blobstore'] = factory(url.path)

    # Create
    create_directory(url.path)


def create_directory(path):
    """ Check if a directory exists for the given path and create it if
    necessary.

    :param path: Absoulte path for of the directory
    :type path:
    """

    if os.path.isdir(path):
        return
    else:
        os.makedirs(path, 0700)
        log.info("Directory %s created".format(path))


def split_by_n(seq, n=2):
    """ A generator to divide a sequence into chunks of n units.

    :param seq: Sequence to be divided
    :type seq: iteratable (usually str)

    :param n: length of chunks
    :type n: int

    :result: list of chunks
    :rtype: iterable
    """

    while seq:
        yield seq[:n]
        seq = seq[n:]


class filestore(object):
    """ BLOB storage provider for Kotti """

    implements(IBlobStorage)

    def __init__(self, path):
        """ The constructor is (optionally) passed a string containing the
        desired configuration options (see above).

        :param config: Configuration string
        :type config: str
        """

        self._path = path

    def path(self, id='tmp'):
        """ Return the absolute path for the given file id.

        :param id: ID of the file object
        :type id: something convertable to unicode

        :result: Full path of the file
        :rtype: unicode
        """

        path = ""

        if id == "tmp":
            path = unicode(id)
        else:
            # Create path from id by converting to unicode,
            # splitting up and inserting slashes
            for subdir in split_by_n(unicode(id).replace("-", "")):
                if path != "":
                    path += "/"
                path += subdir

        #Full path is the newly created path appended to the base directory

        return os.path.join(self._path, path)

    def read(self, id):
        """ Get the data for an object with the given ID.

        :param id: ID of the file object
        :type id: unicode

        :result: Data / value of the file object
        :rtype:
        """

        f = open_file(self.path(id), mode='r')

        return f.read()

    def write(self, data):
        """ Create or update an object with the given ``id`` and write ``data``
        to its contents.

        :param data: Data / value of the file object
        :type data: ???

        :result: ID for the file object
        :rtype: str
        """

        id = uuid4()
        # TODO: call create_directory during transaction
        # check if the filepath and the tempdir exist and create if necessary
        create_directory(os.path.split(self.path(id))[0])
        create_directory(self.path())
        f = create_file(self.path(id), mode='w', tempdir=self.path())
        f.write(data)
        f.close()

        return str(id)

    def remove_base_directory(self, path):
        """ Recursively remove all empty directorys. """

        # Stop if either the base directory is reached
        # or the directory is not empty
        if path == self._path or path+"/" == self._path:
            return
        elif len(os.listdir(path)) > 0:
            return
        else:
            os.rmdir(path)
            self.remove_base_directory(os.path.split(path)[0])

    def delete(self, id):
        """ Delete the object with the given ID.

        :param id: ID of the file object
        :type id: unicode

        :result: Success
        :rtype: bool
        """

        # The kotti.events.ObjectDelete Event fires when the transaction is
        # already committing. It is safe to use os.unlink
        if transaction.get().status == "Committing":
            os.unlink(self.path(id))
            self.remove_base_directory(os.path.split(self.path(id=id))[0])
        else:
            # TODO: call remove_base_directory during transaction
            delete_file(self.path(id))
