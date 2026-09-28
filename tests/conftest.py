"""Test configuration for the plugin repository."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

TEST_ROOT = Path(tempfile.mkdtemp(prefix="gbd-plugin-repo-tests-"))
os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{TEST_ROOT / 'plugin.db'}"
os.environ["GBD_PLUGIN_PATH"] = str(TEST_ROOT / "dl")
os.environ["GBD_ICON_PATH"] = str(TEST_ROOT / "icons")
os.environ["SECRET_KEY"] = "test-secret-key"

from repo import app, db
from repo.models import User


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_root():
    yield
    shutil.rmtree(TEST_ROOT)


@pytest.fixture(autouse=True)
def database():
    app.config.update(TESTING=True)
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        user = User(name="admin", superuser=True)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def runner():
    return app.test_cli_runner()


def csrf_token(client, path):
    """Load a page and extract its CSRF token."""
    response = client.get(path)
    body = response.get_data(as_text=True)
    marker = 'name="csrf_token" value="'
    start = body.index(marker) + len(marker)
    return body[start : body.index('"', start)]


@pytest.fixture
def login(client):
    def do_login():
        token = csrf_token(client, "/login")
        return client.post(
            "/login",
            data={"username": "admin", "password": "password123", "csrf_token": token},
            follow_redirects=False,
        )

    return do_login
