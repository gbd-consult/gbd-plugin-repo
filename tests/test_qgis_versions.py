"""QGIS maximum-version fallback and data-maintenance tests."""

import io
from pathlib import Path
from zipfile import ZipFile

from repo import app, db
from repo.models import Plugin, User, qgis_maximum_version_for
from repo.upload import plugin_upload


def plugin_archive(qgis_minimum_version="3.0", qgis_maximum_version=None):
    metadata = """[general]
name=Test Plugin
version=1.0.0
qgisMinimumVersion={qgis_minimum_version}
description=Test plugin
about=Test plugin
author=Test Author
email=test@example.invalid
repository=https://example.invalid
""".format(
        qgis_minimum_version=qgis_minimum_version
    )
    if qgis_maximum_version:
        metadata += f"qgisMaximumVersion={qgis_maximum_version}\n"

    archive = io.BytesIO()
    with ZipFile(archive, "w") as zip_file:
        zip_file.writestr("test_plugin/metadata.txt", metadata)
    archive.seek(0)
    return archive


def admin_user():
    return User.query.filter_by(name="admin").one()


def test_upload_uses_qgis_minimum_version_major_as_fallback():
    success, _ = plugin_upload(admin_user(), plugin_archive())

    assert success
    assert Plugin.query.one().qgismaximumversion == "3.99"


def test_upload_uses_qgis_4_fallback_for_qgis_4_minimum_version():
    success, _ = plugin_upload(admin_user(), plugin_archive("4.0"))

    assert success
    assert Plugin.query.one().qgismaximumversion == "4.99"


def test_upload_keeps_explicit_qgis_maximum_version():
    success, _ = plugin_upload(
        admin_user(), plugin_archive(qgis_maximum_version="3.28")
    )

    assert success
    assert Plugin.query.one().qgismaximumversion == "3.28"


def test_qgis_4_query_excludes_qgis_3_plugin_without_maximum_version(client):
    success, _ = plugin_upload(admin_user(), plugin_archive("3.0"))
    assert success

    response = client.get("/plugins.xml?qgis=4.0")

    assert response.status_code == 200
    assert b"Test Plugin" not in response.data


def test_maintenance_command_synchronizes_archive_metadata(runner):
    plugin_path = Path(app.config["GBD_PLUGIN_PATH"])
    implicit_archive = plugin_path / "implicit.zip"
    explicit_archive = plugin_path / "explicit.zip"
    implicit_archive.write_bytes(plugin_archive().getvalue())
    explicit_archive.write_bytes(plugin_archive("3.0", "3.28").getvalue())

    implicit = Plugin(
        md5_sum="a" * 32,
        file_name=implicit_archive.name,
        user_id=admin_user().id,
        name="Implicit",
        qgisminimumversion="3.0",
        qgismaximumversion="4.99",
        description="Test",
        about="Test",
        version="1.0",
        author="Test",
        email="test@example.invalid",
        repository="https://example.invalid",
    )
    explicit = Plugin(
        md5_sum="b" * 32,
        file_name=explicit_archive.name,
        user_id=admin_user().id,
        name="Explicit",
        qgisminimumversion="3.0",
        qgismaximumversion="4.99",
        description="Test",
        about="Test",
        version="1.0",
        author="Test",
        email="test@example.invalid",
        repository="https://example.invalid",
    )
    db.session.add_all([implicit, explicit])
    db.session.commit()

    result = runner.invoke(args=["sync-qgis-maximum-versions", "--dry-run"])
    assert result.exit_code == 0
    assert "Would update 2 plugin(s); skipped 0 plugin(s)." in result.output
    assert Plugin.query.filter_by(name="Implicit").one().qgismaximumversion == "4.99"

    result = runner.invoke(args=["sync-qgis-maximum-versions"])
    assert result.exit_code == 0
    assert "Updated 2 plugin(s); skipped 0 plugin(s)." in result.output
    assert Plugin.query.filter_by(
        name="Implicit"
    ).one().qgismaximumversion == qgis_maximum_version_for("3.0")
    assert Plugin.query.filter_by(name="Explicit").one().qgismaximumversion == "3.28"
