import os

# Path where the Plugins are stored
GBD_PLUGIN_PATH = os.getenv("GBD_PLUGIN_PATH", "/data/dl")

GBD_ICON_PATH = os.getenv("GBD_ICON_PATH", "/data/icons/")

# ROOT URI for Plugin Download
# GBD_PLUGIN_ROOT = os.getenv("GBD_PLUGIN_ROOT", "http://localhost:8234/dl")

# Secret key for the app
SECRET_KEY = os.getenv("SECRET_KEY", "notasecret")

# DB Config
SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite:////data/plugin.db"
)


# LDAP
LDAP_HOST = os.getenv("LDAP_HOST")
LDAP_PORT = os.getenv("LDAP_PORT", 389)
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN")
LDAP_USER_DN = os.getenv("LDAP_USER_DN", "ou=users")
LDAP_GROUP_DN = os.getenv("LDAP_GROUP_DN", "ou=groups")
LDAP_USER_RDN_ATTR = os.getenv("LDAP_USER_RDN_ATTR", "cn")
LDAP_USER_LOGIN_ATTR = os.getenv("LDAP_USER_LOGIN_ATTR", "cn")
LDAP_BIND_USER_DN = os.getenv("LDAP_BIND_USER_DN", None)
LDAP_BIND_USER_PASSWORD = os.getenv("LDAP_BIND_USER_PASSWORD", None)
LDAP_GROUP_MEMBERS_ATTR = os.getenv("LDAP_GROUP_MEMBERS_ATTR", "memberOf")
