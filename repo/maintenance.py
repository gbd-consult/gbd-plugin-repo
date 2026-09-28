"""Maintenance commands for existing plugin repository data."""

from configparser import ConfigParser
from configparser import Error as ConfigParserError
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import click

from repo import app, db
from repo.models import Plugin, qgis_maximum_version_for


def plugin_archive_path(plugin):
    """Return the on-disk path for a plugin archive."""
    return Path(app.root_path) / Path(app.config["GBD_PLUGIN_PATH"]) / plugin.file_name


def qgis_versions_from_metadata(archive_path):
    """Read QGIS compatibility versions from a plugin archive."""
    with ZipFile(archive_path) as archive:
        metadata_files = [
            member for member in archive.namelist() if member.endswith("metadata.txt")
        ]
        if len(metadata_files) != 1:
            raise ValueError("archive does not contain exactly one metadata.txt")

        metadata = ConfigParser()
        with archive.open(metadata_files[0]) as metadata_file:
            metadata.read_file((line.decode() for line in metadata_file.readlines()))

    minimum_version = metadata.get("general", "qgisMinimumVersion")
    maximum_version = metadata.get("general", "qgisMaximumVersion", fallback="")
    if not maximum_version:
        maximum_version = qgis_maximum_version_for(minimum_version)

    return minimum_version, maximum_version


@click.command("sync-qgis-maximum-versions")
@click.option("--dry-run", is_flag=True, help="Report changes without committing them.")
def sync_qgis_maximum_versions(dry_run):
    """Synchronize stored maximum versions with plugin archive metadata."""
    updated = 0
    skipped = 0

    for plugin in Plugin.query.all():
        archive_path = plugin_archive_path(plugin)
        try:
            _, maximum_version = qgis_versions_from_metadata(archive_path)
        except (
            BadZipFile,
            ConfigParserError,
            OSError,
            UnicodeDecodeError,
            ValueError,
        ) as error:
            skipped += 1
            click.echo(f"Skipping {plugin.file_name}: {error}")
            continue

        if plugin.qgismaximumversion == maximum_version:
            continue

        old_maximum_version = plugin.qgismaximumversion
        if not dry_run:
            plugin.qgismaximumversion = maximum_version
        updated += 1
        click.echo(
            f"Updating {plugin.file_name}: {old_maximum_version} -> {maximum_version}"
        )

    if updated and not dry_run:
        db.session.commit()

    action = "Would update" if dry_run else "Updated"
    click.echo(f"{action} {updated} plugin(s); skipped {skipped} plugin(s).")


app.cli.add_command(sync_qgis_maximum_versions)
