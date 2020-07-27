"""Helper functions."""
import hashlib
from repo.models import Plugin, User
from sqlalchemy.exc import OperationalError


def readline_generator(fp):
    """Return a generator for readline."""
    line = fp.readline().decode()
    while line:
        yield line
        line = fp.readline().decode()


def dbIsPopulated():
    """Check if our database is already populated."""
    try:
        Plugin.query.all()
        return True
    except OperationalError:
        return False


def createSuperuser():
    """Create a default superuser account."""
    su = User(
        name='admin',
        superuser=True
    )
    su.set_password('admin')
    return su


def md5(file):
    """Return the md5 hash of a file.

    Arguments:
    ---------
        file : file object
            the input file to generate the hash from.

    """
    file.seek(0)
    hash_md5 = hashlib.md5()
    while chunk := file.read(8192):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


def newerVersion(a, b):
    """Return true if the version a is newer than b.

    Argumnents:
    ----------
        a,b : string
            a version string

    """
    return (a != b) and \
        (len(list(filter(lambda x: x[0] < x[1],
                         zip(a.split('.'), b.split('.'))))) == 0)
