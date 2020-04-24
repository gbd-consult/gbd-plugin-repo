from repo import db
from werkzeug.security import generate_password_hash, check_password_hash

class Plugin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    version = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String(120), nullable=False)
    qgis_min_version = db.Column(db.String(10), nullable=False)
    qgis_max_version = db.Column(db.String(10), nullable=False)
    md5_sum = db.Column(db.String(32), nullable=False)
    file_name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return 'Plugin: %s, version %s, zip_file: %s' % (self.name, self.version, self.file_name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(120))
    superuser = db.Column(db.Boolean, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
