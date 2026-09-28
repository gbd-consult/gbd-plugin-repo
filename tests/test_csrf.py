"""CSRF and mutating-route tests."""

from base64 import b64encode

from repo import db
from repo.models import Plugin, Role, User

from .conftest import csrf_token


def test_login_rejects_request_without_csrf_token(client):
    response = client.post(
        "/login", data={"username": "admin", "password": "password123"}
    )

    assert response.status_code == 400


def test_login_accepts_valid_csrf_token(client, login):
    response = login()

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_rejects_external_redirect(client):
    token = csrf_token(client, "/login")
    response = client.post(
        "/login?next=https://example.invalid/",
        data={"username": "admin", "password": "password123", "csrf_token": token},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_accepts_relative_redirect(client):
    token = csrf_token(client, "/login")
    response = client.post(
        "/login?next=/upload",
        data={"username": "admin", "password": "password123", "csrf_token": token},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/upload")


def test_logout_requires_post_and_csrf_token(client, login):
    login()

    assert client.get("/logout").status_code == 405
    assert client.post("/logout").status_code == 400

    token = csrf_token(client, "/")
    response = client.post("/logout", data={"csrf_token": token})

    assert response.status_code == 302


def test_delete_user_requires_post_and_csrf_token(client, login):
    with db.session.no_autoflush:
        user = User(name="other-user", superuser=False)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    login()
    assert client.get(f"/user/{user_id}/delete").status_code == 405
    assert client.post(f"/user/{user_id}/delete").status_code == 400

    token = csrf_token(client, "/users")
    response = client.post(f"/user/{user_id}/delete", data={"csrf_token": token})

    assert response.status_code == 302
    assert User.query.get(user_id) is None


def test_delete_role_requires_post_and_csrf_token(client, login):
    role = Role(name="role-to-delete")
    db.session.add(role)
    db.session.commit()
    role_id = role.id

    login()
    assert client.get(f"/role/{role_id}/delete").status_code == 405
    assert client.post(f"/role/{role_id}/delete").status_code == 400

    token = csrf_token(client, "/roles")
    response = client.post(f"/role/{role_id}/delete", data={"csrf_token": token})

    assert response.status_code == 302
    assert Role.query.get(role_id) is None


def test_xmlrpc_requires_basic_authentication(client, login):
    login()

    assert client.post("/rpc", data=b"<methodCall></methodCall>").status_code == 401

    authorization = b64encode(b"admin:password123").decode()
    response = client.post(
        "/rpc",
        data=b"<methodCall></methodCall>",
        headers={"Authorization": f"Basic {authorization}"},
    )

    assert response.status_code == 200
