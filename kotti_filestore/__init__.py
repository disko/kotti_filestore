# -*- coding: utf-8 -*-

"""
Created on 2014-07-26
:author: Andreas Kaiser (disko)
"""

import os
from uuid import uuid4
from logging import getLogger

from yurl import URL
from zope.interface import implements

from kotti.events import ObjectDelete
from kotti.events import subscribe
from kotti.interfaces import IBlobStorage
from kotti.resources import File
from pyramid.util import DottedNameResolver
from repoze.filesafe import create_file
from repoze.filesafe import delete_file
from repoze.filesafe import open_file
import transaction


log = getLogger(__name__)


def kotti_configure(settings):
    """"""

    url = URL(settings['kotti.blobstore'])

    factory = DottedNameResolver(None).resolve(url.scheme)

    settings['kotti.blobstore'] = factory(url.path)
    createbasefolder(url.path)


def createbasefolder(path):
    """Check if folder for file storage exists and create it if necessary."""
    if os.path.isdir(path):
        return
    else:
        os.makedirs(path)
        log.info("Directory %s created".format(path))


def split_by_n(seq, n=2):
    """A generator to divide a sequence into chunks of n units."""

    while seq:
        yield seq[:n]
        seq = seq[n:]


class filestore(object):
    """"""

    implements(IBlobStorage)

    def __init__(self, path):
        """ The constructor is (optionally) passed a string containing the
        desired configuration options (see above).

        :param config: Configuration string
        :type config: str
        """

        self._path = path

    def path(self, id='tmp'):
        """
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
        # TODO: call createbasefolder during transaction
        # check if the filepath and the tempdir exist and create if necessary
        createbasefolder(os.path.split(self.path(id))[0])
        createbasefolder(self.path())
        f = create_file(self.path(id), mode='w', tempdir=self.path())
        f.write(data)
        f.close()

        return str(id)

    def removebasefolder(self, path):
        """ Recursively remove all empty folders. """
        # Stop if either the base directory is reached
        # or the directory is not empty
        if path == self._path or path+"/" == self._path:
            return
        elif len(os.listdir(path)) > 0:
            return
        else:
            os.rmdir(path)
            self.removebasefolder(os.path.split(path)[0])

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
            self.removebasefolder(os.path.split(self.path(id=id))[0])
        else:
            # TODO: call removebasefolder during transaction
            delete_file(self.path(id))
