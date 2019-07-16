from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('repo.config')
db = SQLAlchemy(app)

from repo import models, routes

