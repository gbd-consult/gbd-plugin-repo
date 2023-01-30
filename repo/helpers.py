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


def newer_version(a, b):
    """Return true if the version a is newer than b.

    Arguments:
    ---------
        a : string
            version string a (if this is newer return true)
        b : string
            version string b

    """
    a_split = [int(x) for x in a.split('.')]
    b_split = [int(x) for x in b.split('.')]
    a_split = a_split + [0] * (len(b_split) - len(a_split))
    b_split = b_split + [0] * (len(a_split) - len(b_split))
    for (a_value, b_value) in zip(a_split, b_split):
        if a_value > b_value:
            return True
    return False
