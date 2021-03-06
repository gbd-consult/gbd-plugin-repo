import os

# Path where the Plugins are stored
GBD_PLUGIN_PATH = os.getenv('GBD_PLUGIN_PATH', '/data/dl')
# ROOT URI for Plugin Download
GBD_PLUGIN_ROOT = os.getenv('GBD_PLUGIN_ROOT', 'http://localhost:8234/dl')
# Secret key for the app
SECRET_KEY = os.getenv('SECRET_KEY','notasecret')

#DB Config
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
    'sqlite:////data/plugin.db')
