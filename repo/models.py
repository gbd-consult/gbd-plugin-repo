"""Database Models."""
from datetime import datetime

from flask import url_for
from flask_login import UserMixin
from lxml import etree
from werkzeug.security import check_password_hash, generate_password_hash

from repo import db

plugin_role_permissions_association = db.Table(
    "plugin_role",
    db.Column("plugin_id", db.Integer, db.ForeignKey("plugin.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
)
plugin_tag_association = db.Table(
    "plugin_tag",
    db.Column("plugin_id", db.Integer, db.ForeignKey("plugin.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class Plugin(db.Model):
    """Model for our QGIS Plugins."""

    id = db.Column(db.Integer, primary_key=True)
    md5_sum = db.Column(db.String(32), nullable=False)
    file_name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    create_date = db.Column(db.DateTime(), default=datetime.utcnow())
    update_date = db.Column(
        db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    public = db.Column(db.Boolean(), default=False)
    roles = db.relationship(
        "Role",
        secondary=plugin_role_permissions_association,
        lazy="subquery",
        backref=db.backref("plugins", lazy=True),
    )
    trusted = db.Column(db.Boolean(), default=True)
    average_votes = db.Column(db.Float(), default=0)
    rating_votes = db.Column(db.Integer(), default=0)
    downloads = db.Column(db.Integer(), default=0)

    # values from metadata.txt
    name = db.Column(db.String(120), nullable=False)
    qgisminimumversion = db.Column(db.String(10), nullable=False)
    qgismaximumversion = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    about = db.Column(db.String(), nullable=False)
    version = db.Column(db.String(10), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    repository = db.Column(db.String(200), nullable=False)
    homepage = db.Column(db.String(200))
    tracker = db.Column(db.String(200))
    changelog = db.Column(db.String())
    experimental = db.Column(db.Boolean(), default=False)
    deprecated = db.Column(db.Boolean(), default=False)
    tags = db.relationship(
        "Tag",
        secondary=plugin_tag_association,
        lazy="subquery",
        backref=db.backref("plugins", lazy=True),
    )
    icon = db.Column(db.String(120))
    plugin_dependencies = db.Column(db.String())
    server = db.Column(db.Boolean(), default=False)
    hasprocessingprovider = db.Column(db.Boolean(), default=False)
    category = db.Column(db.String(20))

    def __repr__(self):
        """Show a Representation of the Plugin."""
        return (
            f"Plugin: {self.name}, version {self.version}, zip_file: {self.file_name}"
        )

    def to_xml(self):
        plugin_element = etree.Element(
            "pyqgis_plugin", version=self.version, name=self.name
        )
        for c_name in [c.name for c in self.__table__.columns]:
            if c_name == "plugin_dependencies":
                element_name = "external_dependencies"
            elif c_name == "qgisminimumversion":
                element_name = "qgis_minimum_version"
            elif c_name == "qgismaximumversion":
                element_name = "qgis_maximum_version"
            elif c_name == "user_id":
                element_name = "uploaded_by"
            else:
                element_name = c_name

            sub_element = etree.SubElement(plugin_element, element_name)

            if c_name == "plugin_dependencies" and not self.plugin_dependencies:
                continue
            elif c_name == "user_id":
                sub_element.text = self.user.name
            else:
                sub_element.text = str(getattr(self, c_name))

        # custom
        url_element = etree.SubElement(plugin_element, "download_url")
        url_element.text = url_for(
            "download_plugin", filename=self.file_name, _external=True
        )

        tags_element = etree.SubElement(plugin_element, "tags")
        tags_element.text = ",".join([str(t) for t in self.tags])

        return plugin_element

    def has_access(self, user):
        return (
            self.public
            or (user.is_authenticated and user.superuser)
            or (user.is_authenticated and set(self.roles).intersection(set(user.roles)))
        )


user_role_association = db.Table(
    "user_role",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    """Model for our users."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(120))
    superuser = db.Column(db.Boolean, nullable=False)
    plugins = db.relationship("Plugin", backref="user", lazy=True)
    roles = db.relationship(
        "Role",
        secondary=user_role_association,
        lazy="subquery",
        backref=db.backref("users", lazy=True),
    )

    def set_password(self, password):
        """Set the password for the user."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the users password."""
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        """Show a Representation of the Tag."""
        return f"{self.name}"
