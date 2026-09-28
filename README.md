# gbd-plugin-repo
A small flask app to serve our QGIS plugin repository at https://plugins.gbd-consult.de
It allows registered users to upload plugins via a web interface.
Only the newest version of a plugin is kept, so users need to be cautious of what to upload.

Eine kleine Flask Anwendung, die unser QGIS Plugin Repository unter https://plugins.gbd-consult.de bereit stellt.
Registrierte Nutzer:innen können Plugins über das Webinterface hochladen.
Es wird nur die neuste Version eines jeden Plugins behalten. Nutzer:innen müssen also aufpassen, was sie hochladen.

## Development without Docker
To run a development version of the app first clone the repository.
```
git clone https://github.com/gbd-consult/gbd-plugin-repo.git
cd gbd-plugin-repo
```
Afterwards install the dependencies with pip.
```
pip install -r requirements.txt
```
Now you can run the development server using:
```
FLASK_APP=repo FLASK_ENV=development flask run
```
You can now brose to `localhost:5000` and login with the credentials: `admin/admin`.

## Docker

Create a docker-compose.yml from the default.
```
cp docker-compose_default.yml docker-compose.yml
```
Build and run the image using
```
docker-compose up --build
```
Browse to localhost:8234

Enjoy! 🛰️

## QGIS maximum-version maintenance

Plugins uploaded without a `qgisMaximumVersion` in their `metadata.txt` default
to QGIS 4.99. To correct existing records that used the former implicit 3.99
default, first run the maintenance command against a current backup with a dry
run:

```
docker compose exec pluginrepo flask --app repo update-qgis-maximum-versions --dry-run
```

After reviewing the output, run the same command without `--dry-run`. The
command only updates archives that do not explicitly declare a maximum version;
plugins declaring `qgisMaximumVersion=3.99` remain unchanged.
