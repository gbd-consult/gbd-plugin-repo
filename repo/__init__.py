"""A small Flask app to serve our QGIS Plugin Repository."""
import logging
import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from repo.rpc import HTTPAuthXMLRPCHandler

app = Flask(__name__)
if app.config["DEBUG"]:
    app.config.from_object("repo.config_dev")
else:
    app.config.from_object("repo.config")

# Setup logging with gunicorn
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

rpc_handler = HTTPAuthXMLRPCHandler("rpc")
rpc_handler.connect(app, "/rpc")

from repo import auth, models, plugins
# on a fresh DB run create_all
from repo.helpers import create_superuser, db_is_populated

if not db_is_populated():
    print("no database found, generating new one")
    if not os.path.isdir(app.config["GBD_PLUGIN_PATH"]):
        os.makedirs(app.config["GBD_PLUGIN_PATH"])
    if not os.path.isdir(app.config["GBD_ICON_PATH"]):
        os.makedirs(app.config["GBD_ICON_PATH"])
    db.create_all()
    su = create_superuser()
    db.session.add(su)
    db.session.commit()
