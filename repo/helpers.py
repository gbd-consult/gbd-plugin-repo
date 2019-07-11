# Helper functions
import hashlib
from zipfile import ZipFile
from repo import models
import os
from configparser import ConfigParser

def readline_generator(fp):
    line = fp.readline().decode()
    while line:
        yield line
        line = fp.readline().decode()


def md5(filename):
    """ Returns the md5 hash of a file.
    Args:
        filename (String): path of the file.
    """
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def extractPluginMetadata(filename, download_root):
    """ Extracts the metadata of a plugin from a zip file.
    Args:
        filename (String): path of the zip file.
        download_root (String): root url to where the zip files can be downloaded from.
    """
    zf = ZipFile(filename)
    metadataFiles = list(filter(lambda x: x.endswith('/metadata.txt'), zf.namelist()))
    if len(metadataFiles) == 1:
        metadata = zf.open(metadataFiles.pop())

        config = ConfigParser()
        config.read_file(readline_generator(metadata))

        plugin = models.Plugin(
            name = config.get('general', 'name'),
            version = config.get('general', 'version'),
            description = config.get('general', 'description'),
            qgis_min_version = config.get('general', 'qgisMinimumVersion'),
            qgis_max_version = config.get('general', 'qgisMaximumVersion'),
            author_name = config.get('general', 'author'),
            file_name = os.path.basename(filename),
            download_url = os.path.join(download_root, os.path.basename(filename)),
            md5_sum = md5(filename))
        return plugin
    else:
        return False
