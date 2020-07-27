"""Database Models."""
from repo import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Plugin(db.Model):
    """Model for our QGIS Plugins."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    version = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String(120), nullable=False)
    qgis_min_version = db.Column(db.String(10), nullable=False)
    qgis_max_version = db.Column(db.String(10), nullable=False)
    md5_sum = db.Column(db.String(32), nullable=False)
    file_name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    repository = db.Column(db.String(200))
    about = db.Column(db.String())
    updated_at = db.Column(db.DateTime(),
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def __repr__(self):
        """Show a Representation of the Plugin."""
        return 'Plugin: %s, version %s, zip_file: %s' \
            % (self.name, self.version, self.file_name)


class User(UserMixin, db.Model):
    """Model for our users."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(120))
    superuser = db.Column(db.Boolean, nullable=False)
    plugins = db.relationship('Plugin', backref='user', lazy=True)

    def set_password(self, password):
        """Set the password for the user."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the users password."""
        return check_password_hash(self.password_hash, password)
