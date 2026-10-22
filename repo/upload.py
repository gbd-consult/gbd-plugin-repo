"""Validate and register QGIS and QField plugin packages."""
import io
from configparser import Error as ConfigParserError
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile

from flask import url_for
from packaging.version import Version
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from repo import app, db
from repo.helpers import md5
from repo.metadata import read_metadata
from repo.models import Plugin, PluginDetails, Tag, User, qgis_maximum_version_for


def plugin_upload(user: User, package: io.BytesIO, platform="qgis", filename=None):
    if platform not in {"qgis", "qfield"}:
        return False, "Unknown plugin platform."
    checksum = md5(package)
    if Plugin.for_platform(platform).filter(Plugin.md5_sum == checksum).first():
        return False, "uploaded Plugin is a duplicate!"

    try:
        with ZipFile(package) as archive:
            values, root, members = read_metadata(archive)
            required = ["name", "version", "description", "author"]
            if platform == "qgis":
                required += ["qgisminimumversion", "about", "email", "repository"]
                if "main.qml" in members:
                    raise ValueError(
                        "This is a QField package. Please use QField Plugins."
                    )
            elif "main.qml" not in members or str(root) != ".":
                raise ValueError(
                    "QField ZIPs must contain main.qml and metadata.txt at the ZIP root."
                )
            missing = [key for key in required if not values.get(key, "").strip()]
            if missing:
                raise ValueError("Missing metadata fields: " + ", ".join(missing))
            Version(values["version"])
            if platform == "qgis":
                minimum = values["qgisminimumversion"]
                maximum = values.get("qgismaximumversion") or qgis_maximum_version_for(
                    minimum
                )
                if Version(minimum) > Version(maximum):
                    raise ValueError(
                        "qgisMaximumVersion must not be below qgisMinimumVersion."
                    )
            else:
                minimum = maximum = "0.0"
            if platform == "qgis" and root.name:
                stem = root.name
            elif filename:
                stem = Path(filename).stem
            else:
                stem = values["name"].lower().replace(" ", "_").replace("-", "_")
            stem = secure_filename(stem)
            if not stem:
                raise ValueError("Invalid plugin package name.")
            package_name = stem + ".zip"
            old_plugin = (
                Plugin.for_platform(platform)
                .filter(Plugin.file_name == package_name)
                .first()
            )
            if old_plugin and Version(old_plugin.version) >= Version(values["version"]):
                return (
                    False,
                    "There already exists the same or a newer version of this plugin.",
                )

            icon_data = None
            if values.get("icon"):
                icon = PurePosixPath(values["icon"])
                if icon.is_absolute() or ".." in icon.parts:
                    raise ValueError("Invalid icon path in metadata.txt.")
                icon_member = str(root / icon)
                if icon_member not in members:
                    raise ValueError(
                        "Icon referenced in metadata.txt is missing from the ZIP."
                    )
                if icon.suffix.lower() not in {
                    ".png",
                    ".svg",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".webp",
                }:
                    raise ValueError("Unsupported plugin icon format.")
                icon_name = stem + icon.suffix.lower()
                icon_data = archive.read(icon_member)
    except (
        BadZipFile,
        ConfigParserError,
        UnicodeDecodeError,
        ValueError,
        KeyError,
        OSError,
    ) as error:
        return False, str(error) or "Invalid plugin ZIP."

    plugin = old_plugin or Plugin()
    # Only metadata fields may be imported; permissions, ownership and counters
    # must never be writable through metadata.txt.
    text_fields = [
        "name",
        "description",
        "about",
        "version",
        "author",
        "email",
        "repository",
        "homepage",
        "tracker",
        "changelog",
        "category",
        "plugin_dependencies",
    ]
    for key in text_fields:
        setattr(plugin, key, values.get(key, ""))
    for key in ["experimental", "deprecated", "server", "hasprocessingprovider"]:
        setattr(plugin, key, values.get(key, "false").lower() in {"true", "yes", "1"})
    plugin.qgisminimumversion = minimum
    plugin.qgismaximumversion = maximum
    plugin.md5_sum = checksum
    plugin.file_name = package_name
    plugin.user_id = user.id
    plugin.details = plugin.details or PluginDetails(platform=platform)
    plugin.details.metadata_values = values
    plugin.tags = []
    for name in dict.fromkeys(
        tag.strip() for tag in values.get("tags", "").split(",") if tag.strip()
    ):
        with db.session.no_autoflush:
            tag = Tag.query.filter_by(name=name).first()
        plugin.tags.append(tag or Tag(name=name))
    subdirectory = "qfield" if platform == "qfield" else ""
    plugin_dir = Path(app.root_path) / app.config["GBD_PLUGIN_PATH"] / subdirectory
    icon_dir = Path(app.root_path) / app.config["GBD_ICON_PATH"] / subdirectory
    if icon_data is not None:
        endpoint = "qfield_icon" if platform == "qfield" else "get_icon"
        plugin.icon = url_for(endpoint, filename=icon_name)
    else:
        plugin.icon = None
    try:
        # Validate the database insert before writing any package files.
        db.session.add(plugin)
        db.session.flush()
        plugin_dir.mkdir(parents=True, exist_ok=True)
        (plugin_dir / package_name).write_bytes(package.getvalue())
        if icon_data is not None:
            icon_dir.mkdir(parents=True, exist_ok=True)
            (icon_dir / icon_name).write_bytes(icon_data)
        db.session.commit()
    except (SQLAlchemyError, OSError):
        db.session.rollback()
        app.logger.exception("Could not store plugin package")
        return False, "Could not save plugin. See server logs for details."
    app.logger.info(f"PLUGIN_UPLOADED: {plugin.name} by {user.name} ({platform})")
    return True, (plugin.id, plugin.version)
