import os
import transaction
from pytest import raises


def test_split():
    """ Test Cases for kotti_filestore.split_by_n(). """

    import kotti_filestore
    teststring = "ABCDEF"
    teststring2 = teststring
    # split_by_n() without second parameter should split the string by 2
    for substring in kotti_filestore.split_by_n(teststring):
        assert substring == teststring[:2]
        teststring = teststring[2:]
    # Testing splitting up by a length of 3
    for substring in kotti_filestore.split_by_n(teststring2, 3):
        assert substring == teststring2[:3]
        teststring2 = teststring2[3:]


def test_path(testfilestore):
    """ Test Cases for filestore.path(). """

    addedstring = "ABCDEF"
    # Test that path() returns the filepath by splitting up addedstring and
    # adding the new path to the initpath
    assert testfilestore.path(addedstring) == "./.testtmp/AB/CD/EF"
    # Without any parameter path() should just add /tmp to the initpath
    assert testfilestore.path() == "./.testtmp/tmp"


def test_createbasefolder(removedir):
    """ Test Cases for kotti_filestore.createbasefolder(). """

    import kotti_filestore

    os.makedirs("./.testtmp/test/")
    # Test that function returns without exception if folder already exists
    kotti_filestore.createbasefolder("./.testtmp/test")
    # Test that new folder is created if specified folder does not exist
    kotti_filestore.createbasefolder("./.testtmp/test2")
    assert os.path.isdir("./.testtmp/test2")


def test_read(removedir, request, testfilestore):
    """ Test Cases for filestore.read(). """

    def rmfile():
        os.unlink("./.testtmp/te/st")
    request.addfinalizer(rmfile)

    testtext = "Testtext\n"
    os.makedirs("./.testtmp/te")
    testfile = open("./.testtmp/te/st", "w")
    # Write into testfile then give id to read() and test that
    # return value equals the value written into file
    testfile.write(testtext)
    testfile.close()
    assert testfilestore.read("test") == testtext


def test_removebasefolder(removedir, testfilestore):
    """ Test Cases for filestore.removebasefolder(). """

    os.makedirs("./.testtmp/te/st/di/re/ct/or/y")
    # Add random content to folder te
    os.mkdir("./.testtmp/te/foldercontent")
    # Test that function returns without exception when path is
    # filestore directory
    testfilestore.removebasefolder("./.testtmp/")
    testfilestore.removebasefolder("./.testtmp/te/st/di/re/ct/or/y")
    # Test that all empty folders have been removed
    assert os.path.isdir("./.testtmp/te/st") is False
    # Test that recursive removal has stopped at non-empty folder
    assert os.path.isdir("./.testtmp/te")


def test_delete(transactionmockup, removedir, testfilestore):
    """ Test Cases for filestore.removebasefolder(). """

    os.makedirs("./.testtmp/te")
    testfile = open("./.testtmp/te/st", "w")
    testfile.write("test")
    testfile.close()
    testfilestore.delete("test")
    # Check that file no longer exists
    assert os.path.isfile("./.testtmp/te/st") is False
    # Check that containing folder no longer exists
    assert os.path.isdir("./.testtmp/te") is False
    # Check that initial folder has not been deleted
    assert os.path.isdir("./.testtmp")


def test_write(db_session, removedir, testfilestore):
    """ Test Cases for filestore.write(). """

    os.mkdir("./.testtmp")
    testfile_id = testfilestore.write("test")
    # Test that file does not exist before the commit
    with raises(IOError):
        testfile = open(testfilestore.path(testfile_id), "r")
    transaction.commit()
    # Test that after committing, file exists and contains correct data
    testfile = open(testfilestore.path(testfile_id), "r")
    assert testfile.read() == "test"
    testfile.close()


def test_configure(removedir):

    import kotti_filestore

    os.mkdir("./.testtmp")
    testsettings = {'kotti.blobstore':
        u'kotti_filestore.filestore:./.testtmp/testfilestore'}
    kotti_filestore.kotti_configure(testsettings)
    assert testsettings['kotti.blobstore']._path == u'./.testtmp/testfilestore'
    assert os.path.isdir("./.testtmp/testfilestore")
