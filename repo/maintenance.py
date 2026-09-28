"""Maintenance commands for existing plugin repository data."""

from configparser import ConfigParser
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import click

from repo import app, db
from repo.models import DEFAULT_QGIS_MAXIMUM_VERSION, Plugin


def plugin_archive_path(plugin):
    """Return the on-disk path for a plugin archive."""
    return Path(app.config["GBD_PLUGIN_PATH"]) / plugin.file_name


def metadata_has_qgis_maximum_version(archive_path):
    """Return whether an archive explicitly defines qgisMaximumVersion."""
    with ZipFile(archive_path) as archive:
        metadata_files = [
            member for member in archive.namelist() if member.endswith("metadata.txt")
        ]
        if len(metadata_files) != 1:
            raise ValueError("archive does not contain exactly one metadata.txt")

        metadata = ConfigParser()
        with archive.open(metadata_files[0]) as metadata_file:
            metadata.read_file((line.decode() for line in metadata_file.readlines()))

    return metadata.has_option("general", "qgisMaximumVersion")


@click.command("update-qgis-maximum-versions")
@click.option("--dry-run", is_flag=True, help="Report changes without committing them.")
def update_qgis_maximum_versions(dry_run):
    """Update former implicit QGIS 3.99 maximum versions to 4.99."""
    updated = 0
    skipped = 0

    plugins = Plugin.query.filter_by(qgismaximumversion="3.99").all()
    for plugin in plugins:
        archive_path = plugin_archive_path(plugin)
        try:
            has_explicit_maximum = metadata_has_qgis_maximum_version(archive_path)
        except (BadZipFile, OSError, UnicodeDecodeError, ValueError) as error:
            skipped += 1
            click.echo(f"Skipping {plugin.file_name}: {error}")
            continue

        if has_explicit_maximum:
            skipped += 1
            click.echo(f"Skipping {plugin.file_name}: explicit qgisMaximumVersion")
            continue

        if not dry_run:
            plugin.qgismaximumversion = DEFAULT_QGIS_MAXIMUM_VERSION
        updated += 1
        click.echo(
            f"Updating {plugin.file_name}: 3.99 -> {DEFAULT_QGIS_MAXIMUM_VERSION}"
        )

    if updated and not dry_run:
        db.session.commit()

    action = "Would update" if dry_run else "Updated"
    click.echo(f"{action} {updated} plugin(s); skipped {skipped} plugin(s).")


app.cli.add_command(update_qgis_maximum_versions)
