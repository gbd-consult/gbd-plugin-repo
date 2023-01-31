import io
from configparser import ConfigParser
from configparser import Error as ConfigParserError
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from repo import app, db
from repo.helpers import md5, newer_version, readline_generator
from repo.models import Plugin, User


def plugin_upload(user: User, package: io.BytesIO):
    existing_plugin = Plugin.query.filter_by(md5_sum=md5(package)).first()
    if existing_plugin:
        return (False, "uploaded Plugin is a duplicate!")

    # Check if we can open the zip file
    try:
        zip_file = ZipFile(package)
    except BadZipFile:
        return (False, "broken zip file!")

    # Check if the zip file contains a metadata.txt file
    metadata_files = list(
        filter(lambda x: x.endswith("metadata.txt"), zip_file.namelist())
    )
    if not len(metadata_files) == 1:
        return (False, "missing metadata.txt")

    metadata_file = metadata_files.pop()

    # Try to read metadata.txt
    try:
        metadata = zip_file.open(metadata_file)
        config = ConfigParser()
        config.read_file(readline_generator(metadata))

        name = config.get("general", "name")
        version = config.get("general", "version")
        description = config.get("general", "description")
        qgis_min_version = config.get("general", "qgisMinimumVersion")
        qgis_max_version = config.get("general", "qgisMaximumVersion", fallback="3.99")
        author_name = config.get("general", "author")
        repository = config.get("general", "repository", fallback="")
        about = config.get("general", "about", fallback="")

    except ConfigParserError:
        return (False, "invalid metadata.txt file")

    # Set package_name
    if Path(metadata_file).parent.name:
        package_name = f"{Path(metadata_file).parent.name}.zip"
    else:
        package_name = f"{name.lower().replace(' ', '_').replace('-', '_')}.zip"

    # close zip file:
    zip_file.close()

    # Check if there already is a plugin with that name
    old_plugin = Plugin.query.filter_by(file_name=package_name).first()
    if old_plugin and not newer_version(version, old_plugin.version):
        return (False, f"There already exists a more recent verion of {package_name}")

    # Write package to disk
    try:
        plugin_path = (
            Path(app.root_path)
            / Path(app.config["GBD_PLUGIN_PATH"])
            / Path(package_name)
        )
        with open(plugin_path, "wb") as out_file:
            out_file.write(package.read())
    except IOError:
        return (False, "writing of plugin failed")

    # modify plugin in db
    if old_plugin:
        plugin = old_plugin
        app.logger.info(
            (
                f"PLUGIN_UPDATED: {name}({plugin.id}) to "
                f"{version} by user {user.name}"
            )
        )
    else:
        plugin = Plugin()
        app.logger.info(f"PLUGIN_CREATED: {name} by user {user.name}")

    plugin.name = name
    plugin.version = version
    plugin.description = description
    plugin.qgis_min_version = qgis_min_version
    plugin.qgis_max_version = qgis_max_version
    plugin.author_name = author_name
    plugin.md5_sum = md5(package)
    plugin.file_name = package_name
    plugin.user_id = user.id
    # optional
    plugin.repository = repository
    plugin.about = about

    db.session.add(plugin)
    db.session.commit()

    return (True, (plugin.id, plugin.version))
