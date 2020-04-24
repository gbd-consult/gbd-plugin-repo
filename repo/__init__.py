from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import os.path

app = Flask(__name__)
if app.config['ENV'] == 'production':
    app.config.from_object('repo.config')
else:
    app.config.from_object('repo.config_dev')

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

from repo import models, routes, authentication

# on a fresh DB run create_all
from repo.helpers import dbIsPopulated, createSuperuser

if not dbIsPopulated():
    db.create_all()
    su = createSuperuser()
    db.session.add(su)
    db.session.commit()
