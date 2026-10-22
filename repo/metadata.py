"""Read metadata shared by the QGIS and QField catalogues."""

from configparser import ConfigParser
from pathlib import PurePosixPath


def archive_members(archive):
    members = []
    for member in archive.namelist():
        path = PurePosixPath(member)
        if member.endswith("/"):
            continue
        if path.is_absolute() or ".." in path.parts or "\\" in member:
            raise ValueError("Invalid path in ZIP archive.")
        members.append(member)
    return members


def read_metadata(archive):
    members = archive_members(archive)
    matches = [member for member in members if member.endswith("metadata.txt")]
    if not matches:
        raise ValueError("Missing metadata.txt in ZIP archive.")
    if len(matches) != 1:
        raise ValueError("ZIP archive contains multiple metadata.txt files.")
    filename = matches[0]
    config = ConfigParser(interpolation=None)
    config.read_string(archive.read(filename).decode("utf-8-sig"))
    return dict(config.items("general")), PurePosixPath(filename).parent, members
