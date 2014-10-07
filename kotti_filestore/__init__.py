# -*- coding: utf-8 -*-

"""
Created on 2014-07-26
:author: Andreas Kaiser (disko)
"""

import os
from uuid import uuid4

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


def kotti_configure(settings):
    """"""

    url = URL(settings['kotti.blobstore'])

    factory = DottedNameResolver(None).resolve(url.scheme)

    settings['kotti.blobstore'] = factory(url.path)
    settings['pyramid.includes'] += ' kotti_filestore'


def includeme(config):
    config.scan(__name__)


def split_by_n(seq, n=2):
    """A generator to divide a sequence into chunks of n units."""

    while seq:
        yield seq[:n]
        seq = seq[n:]


class Filestore(object):
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

        return os.path.join(self._path, unicode(id))

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
        f = create_file(self.path(id), mode='w', tempdir=self.path())
        f.write(data)
        f.close()

        return str(id)

    def delete(self, id):
        """ Delete the object with the given ID.

        :param id: ID of the file object
        :type id: unicode

        :result: Success
        :rtype: bool
        """

        delete_file(self.path(id=id))
