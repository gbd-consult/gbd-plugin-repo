from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)
if app.config['ENV'] == 'production':
    app.config.from_object('repo.config')
else:
    app.config.from_object('repo.config_dev')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from repo import models, routes, auth

# on a fresh DB run create_all
from repo.helpers import dbIsPopulated, createSuperuser

if not dbIsPopulated():
    if not os.path.isdir(app.config['GBD_PLUGIN_PATH']):
        os.makedirs(app.config['GBD_PLUGIN_PATH'])
    db.create_all()
    su = createSuperuser()
    db.session.add(su)
    db.session.commit()
