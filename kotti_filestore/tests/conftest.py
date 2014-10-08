pytest_plugins = "kotti"

from pytest import fixture
import shutil


class mocktransaction(object):
    def __init__(self, status):
        self.status = status


@fixture
def transactionmockup(monkeypatch):

    testtransaction = mocktransaction("Committing")
    monkeypatch.setattr(
        "transaction.get",
        lambda: testtransaction)


@fixture
def removedir(request):
    def rmdir():
        shutil.rmtree("./.testtmp")
    request.addfinalizer(rmdir)


@fixture
def testfilestore():
    from kotti_filestore import filestore
    return filestore("./.testtmp/")
