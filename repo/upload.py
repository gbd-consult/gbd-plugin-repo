import io
from configparser import ConfigParser
from configparser import Error as ConfigParserError
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from flask import url_for
from packaging import version
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import sqltypes

from repo import app, db
from repo.helpers import md5, readline_generator
from repo.models import Plugin, Tag, User


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

        metadata_dict = dict(config.items("general"))
        name = metadata_dict.get("name")
        plugin_version = metadata_dict.get("version")

    except ConfigParserError:
        return (False, "invalid metadata.txt file")

    # Set package_name
    if Path(metadata_file).parent.name:
        package_name = f"{Path(metadata_file).parent.name}.zip"
    else:
        package_name = f"{name.lower().replace(' ', '_').replace('-', '_')}.zip"

    # Save icon if any
    if "icon" in metadata_dict.keys():
        zip_icon_path = Path(package_name).stem / Path(metadata_dict.get("icon"))
        filename = f"{Path(package_name).stem}{Path(metadata_dict.get('icon')).suffix}"
        icon_path = Path(app.config["GBD_ICON_PATH"]) / filename
        with open(icon_path, "wb") as icon_file:
            icon_file.write(zip_file.read(str(zip_icon_path)))
        metadata_dict.update({"icon": url_for("get_icon", filename=filename)})

    # close zip file:
    zip_file.close()

    # Check if there already is a plugin with that name
    old_plugin = Plugin.query.filter_by(file_name=package_name).first()
    if old_plugin and version.parse(old_plugin.version) >= version.parse(
        plugin_version
    ):
        return (
            False,
            f"There already exist a version of the plugin {package_name} that is the same or newer.",
        )

    # Write package to disk
    try:
        plugin_path = (
            Path(app.root_path)
            / Path(app.config["GBD_PLUGIN_PATH"])
            / Path(package_name)
        )
        with open(plugin_path, "wb") as out_file:
            package.seek(0)
            out_file.write(package.read())

    except IOError:
        return (False, "writing of plugin failed")

    # modify plugin in db
    if old_plugin:
        plugin = old_plugin
        mode = "UPDATED"
    else:
        plugin = Plugin()
        mode = "CREATED"

    if "tags" in metadata_dict.keys():
        tag_name_list = metadata_dict.get("tags").split(",")
        tag_list = []
        for tag_name in tag_name_list:
            tag = Tag.query.filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
            tag_list.append(tag)
        db.session.add_all(tag_list)
        db.session.commit()
        metadata_dict.update({"tags": tag_list})

    for key, value in metadata_dict.items():
        if (
            key in [c.name for c in plugin.__table__.columns]
            and isinstance(plugin.__table__.c[key].type, sqltypes.Boolean)
            and not isinstance(value, bool)
        ):
            value = value == "True"
        setattr(plugin, key, value)

    plugin.md5_sum = md5(package)
    plugin.file_name = package_name
    plugin.user_id = user.id

    try:
        db.session.add(plugin)
        db.session.commit()
    except SQLAlchemyError as e:
        app.logger.warning(e.statement)
        app.logger.warning(e.params)
        app.logger.warning(e.orig)
        return (False, "Error creating plugin. See logs for details.")

    app.logger.info(f"PLUGIN_{mode}: {name} by user {user.name}")
    return (True, (plugin.id, plugin.version))
