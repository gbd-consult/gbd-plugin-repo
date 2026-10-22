"""Catalogue separation, permissions, localized metadata and ZIP regressions."""
import io
from base64 import b64encode
from pathlib import Path
from zipfile import ZipFile

import pytest

from repo import app, db
from repo.models import Plugin, PluginDetails, Role, User
from repo.upload import plugin_upload

from .conftest import csrf_token


def archive(
    platform="qgis",
    extra="",
    version="1.0",
    name="Example",
    icon=False,
    folder=None,
):
    metadata = f"""[general]
name={name}
version={version}
description=English description
about=English about
    Second line
about[de]=Deutsche Beschreibung
    Zweite Zeile
changelog=English changes
changelog[de]=Deutsche Änderungen
author=Example Author
"""
    if platform == "qgis":
        metadata += "qgisMinimumVersion=3.34\nemail=test@example.invalid\nrepository=https://example.invalid\n"
    if icon:
        metadata += "icon=icon.svg\n"
    metadata += extra
    root = ("example/" if platform == "qgis" else "") if folder is None else folder
    package = io.BytesIO()
    with ZipFile(package, "w") as zip_file:
        zip_file.writestr(root + "metadata.txt", metadata)
        if platform == "qfield":
            zip_file.writestr(root + "main.qml", "import QtQuick\nItem {}")
        if icon:
            zip_file.writestr(
                root + "icon.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>'
            )
    package.seek(0)
    return package


def upload(platform="qgis", **kwargs):
    with app.test_request_context("/"):
        success, result = plugin_upload(
            User.query.filter_by(name="admin").one(),
            archive(platform, **kwargs),
            platform,
        )
    assert success, result
    return Plugin.query.get(result[0])


def basic(user="admin", password="password123"):
    return {
        "Authorization": "Basic " + b64encode(f"{user}:{password}".encode()).decode()
    }


def test_catalogues_and_xml_are_separate(client):
    upload(name="Desktop example")
    mobile = upload("qfield", name="Mobile example")
    assert b"Desktop example" in client.get("/").data
    assert b"Mobile example" not in client.get("/").data
    assert b"Mobile example" in client.get("/qfield").data
    assert b"Desktop example" not in client.get("/qfield").data
    feed = client.get("/plugins.xml").data
    assert b"Desktop example" in feed and b"Mobile example" not in feed
    assert b"metadata_values" not in feed
    assert client.get(f"/qfield/download/{mobile.file_name}").status_code == 200
    assert client.get(f"/download/{mobile.file_name}").status_code == 404


@pytest.mark.parametrize("platform", ["qgis", "qfield"])
def test_private_plugin_permissions_apply_to_list_detail_icon_download(
    client, platform
):
    plugin = upload(platform, icon=True)
    role = Role(name="team")
    allowed = User(name="allowed", superuser=False, roles=[role])
    denied = User(name="denied", superuser=False)
    for user in [allowed, denied]:
        user.set_password("password123")
    plugin.public = False
    plugin.roles = [role]
    db.session.add_all([allowed, denied])
    db.session.commit()
    list_url = "/qfield" if platform == "qfield" else "/"
    download = (
        ("/qfield" if platform == "qfield" else "") + "/download/" + plugin.file_name
    )
    for headers, visible in [
        ({}, False),
        (basic("denied"), False),
        (basic("allowed"), True),
        (basic(), True),
    ]:
        assert (b"Example" in client.get(list_url, headers=headers).data) == visible
        for path in [f"/plugin/{plugin.id}", plugin.icon, download]:
            assert client.get(path, headers=headers).status_code == (
                200 if visible else 403
            )
    assert b"Example" not in client.get("/plugins.xml").data


def test_localized_metadata_survives_reload_and_falls_back(client):
    plugin = upload()
    plugin_id = plugin.id
    db.session.remove()
    de = client.get(f"/plugin/{plugin_id}?lang=de").get_data(as_text=True)
    en = client.get(f"/plugin/{plugin_id}?lang=en").get_data(as_text=True)
    assert "Deutsche Beschreibung\nZweite Zeile" in de
    assert "English about\nSecond line" in en
    assert "Deutsche Änderungen" in de and "English changes" in en
    assert "English description" in de  # No German description was supplied.
    assert "Deutsche Beschreibung" not in en
    assert "Deutsche Beschreibung" in client.get(
        f"/plugin/{plugin_id}", headers={"Accept-Language": "de-DE,de;q=0.9"}
    ).get_data(as_text=True)


def test_duplicate_metadata_and_missing_email_fail_before_writing():
    package = archive()
    with ZipFile(package, "a") as zip_file:
        zip_file.writestr("another/metadata.txt", "[general]\nname=Other")
    success, message = plugin_upload(User.query.one(), package)
    assert not success and "multiple" in message
    package = io.BytesIO()
    with ZipFile(package, "w") as zip_file:
        zip_file.writestr(
            "missing_email/metadata.txt",
            "[general]\nname=Missing\nversion=1.0\nauthor=Me\ndescription=Text\nabout=Text\nqgisMinimumVersion=3.34\nrepository=https://example.invalid",
        )
    success, message = plugin_upload(User.query.one(), package)
    assert not success and "email" in message
    assert not (Path(app.config["GBD_PLUGIN_PATH"]) / "missing_email.zip").exists()
    assert Plugin.query.count() == 0


def test_metadata_cannot_grant_permissions_or_overwrite_internal_fields():
    plugin = upload(
        extra="public=False\nuser_id=999\ndownloads=100000\nplatform=qfield\n"
    )
    assert plugin.public and plugin.user_id == User.query.one().id
    assert plugin.downloads == 0 and plugin.platform == "qgis"


def test_update_preserves_visibility_and_roles_and_rejects_downgrade():
    plugin = upload("qfield")
    plugin.public = False
    plugin.roles = [Role(name="restricted")]
    db.session.commit()
    plugin = upload("qfield", version="2.0")
    assert not plugin.public and plugin.roles[0].name == "restricted"
    success, _ = plugin_upload(
        User.query.one(), archive("qfield", version="1.5"), "qfield"
    )
    assert not success
    assert Plugin.query.one().version == "2.0"


def test_same_archive_filename_on_different_platforms_does_not_collide(client):
    desktop = upload(folder="example/")
    desktop_filename = desktop.file_name
    mobile = upload("qfield")
    assert desktop_filename == mobile.file_name == "example.zip"
    assert (
        client.get("/download/example.zip").data
        != client.get("/qfield/download/example.zip").data
    )


def test_qfield_upload_csrf_and_privileges(client, login):
    assert client.get("/qfield/upload").status_code == 302
    regular = User(name="regular", superuser=False)
    regular.set_password("password123")
    db.session.add(regular)
    db.session.commit()
    assert client.get("/qfield/upload", headers=basic("regular")).status_code == 403
    login()
    assert (
        client.post(
            "/qfield/upload", data={"file": (archive("qfield"), "example.zip")}
        ).status_code
        == 400
    )
    token = csrf_token(client, "/qfield/upload")
    response = client.post(
        "/qfield/upload",
        data={"csrf_token": token, "file": (archive("qfield"), "example.zip")},
    )
    assert response.status_code == 302
    assert response.location.endswith("/qfield/upload")
    assert Plugin.query.one().platform == "qfield"


def test_upload_role_can_upload_but_cannot_edit_or_delete(client):
    user = User(name="uploader", superuser=False, roles=[Role(name="upload")])
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    headers = basic("uploader")
    token_response = client.get("/qfield/upload", headers=headers).get_data(
        as_text=True
    )
    token = token_response.split('name="csrf_token" value="')[1].split('"')[0]
    response = client.post(
        "/qfield/upload",
        headers=headers,
        data={"csrf_token": token, "file": (archive("qfield"), "example.zip")},
    )
    assert response.status_code == 302
    plugin = Plugin.query.one()
    for path in [f"/plugin/{plugin.id}/edit", f"/plugins/{plugin.id}/delete"]:
        assert (
            client.post(path, headers=headers, data={"csrf_token": token}).status_code
            == 403
        )


def test_qfield_rejects_qgis_folder_structure():
    success, message = plugin_upload(
        User.query.one(), archive("qfield", folder="nested/"), "qfield"
    )
    assert not success and "ZIP root" in message


def test_existing_records_without_details_remain_qgis(client):
    plugin = upload()
    db.session.delete(plugin.details)
    db.session.commit()
    db.session.expire_all()
    assert Plugin.query.one().platform == "qgis"
    assert b"Example" in client.get("/").data
    assert PluginDetails.query.count() == 0


def test_private_qfield_visibility_edit_and_delete(client, login):
    plugin = upload("qfield")
    plugin_id = plugin.id
    filename = plugin.file_name
    login()
    token = csrf_token(client, f"/plugin/{plugin_id}")
    assert (
        client.post(f"/plugin/{plugin_id}/edit", data={"csrf_token": token}).status_code
        == 302
    )
    assert not Plugin.query.get(plugin_id).public
    assert client.get(f"/plugins/{plugin_id}/delete").status_code == 405
    assert client.post(f"/plugins/{plugin_id}/delete").status_code == 400
    assert client.post(
        f"/plugins/{plugin_id}/delete", data={"csrf_token": token}
    ).location.endswith("/qfield")
    assert PluginDetails.query.count() == 0
    assert not (Path(app.config["GBD_PLUGIN_PATH"]) / "qfield" / filename).exists()


def test_documentation_placeholder_and_configured_target(client, monkeypatch):
    assert b"Dokumentation" in client.get("/documentation").data
    monkeypatch.setitem(
        app.config, "DOCUMENTATION_URL", "https://docs.example.invalid/"
    )
    assert client.get("/documentation").location == "https://docs.example.invalid/"


def test_legacy_database_startup_adds_table_without_recreating_admin(tmp_path):
    import os
    import sqlite3
    import subprocess
    import sys

    legacy = tmp_path / "legacy.db"
    source = sqlite3.connect(
        Path(app.config["SQLALCHEMY_DATABASE_URI"].removeprefix("sqlite:///"))
    )
    destination = sqlite3.connect(legacy)
    source.backup(destination)
    destination.execute("DROP TABLE plugin_details")
    destination.commit()
    destination.close()
    source.close()
    env = dict(
        os.environ, SQLALCHEMY_DATABASE_URI=f"sqlite:///{legacy}", FLASK_DEBUG="0"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from repo import db; from repo.models import User, PluginDetails; assert User.query.count() == 1; assert PluginDetails.query.count() == 0",
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_root_metadata_icon_and_literal_percent_text(client):
    plugin = upload(
        folder="", icon=True, extra="homepage=https://example.invalid/100%25\n"
    )
    assert client.get(plugin.icon).status_code == 200
    assert plugin.homepage == "https://example.invalid/100%25"


def test_missing_icon_does_not_save_package():
    success, message = plugin_upload(
        User.query.one(), archive(extra="icon=missing.svg\n")
    )
    assert not success and "Icon" in message
    assert Plugin.query.count() == 0


def test_qgis_maintenance_does_not_modify_qfield_versions(runner):
    plugin = upload("qfield")
    result = runner.invoke(args=["sync-qgis-maximum-versions"])
    assert result.exit_code == 0 and "Updated 0" in result.output
    assert Plugin.query.get(plugin.id).qgismaximumversion == "0.0"
