"""Helper functions."""
import hashlib

from sqlalchemy.exc import OperationalError

from repo.models import Plugin, User


def readline_generator(fp):
    """Return a generator for readline."""
    line = fp.readline().decode()
    while line:
        yield line
        line = fp.readline().decode()


def db_is_populated():
    """Check if our database is already populated."""
    try:
        Plugin.query.all()
        return True
    except OperationalError:
        return False


def create_superuser():
    """Create a default superuser account."""
    su = User(name="admin", superuser=True)
    su.set_password("admin")
    return su


def add_vote(current_avg: float, current_votes: int, vote: int):
    """Calculate the new averate rating.

    Arguments:
    ---------
        current_avg: float
            the current average rating.
        current_votes: int
            the current number of votes.
        vote: int
            the vote to be added.
    """
    return (current_avg * current_votes + vote) / (current_votes + 1)


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
