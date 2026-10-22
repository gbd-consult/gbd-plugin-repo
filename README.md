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

QGIS interprets a missing `qgisMaximumVersion` as the end of the major release
line declared by `qgisMinimumVersion`; for example, `3.4` implies `3.99`. The
repository follows the same rule. To synchronize existing repository records
with the metadata embedded in their plugin archives, first run the maintenance
command against a current backup with a dry run:

```
docker compose exec pluginrepo flask --app repo sync-qgis-maximum-versions --dry-run
```

After reviewing the output, run the same command without `--dry-run`. To make a
QGIS 3 plugin eligible for QGIS 4, add `qgisMaximumVersion=4.99` to its own
`metadata.txt`, test it under QGIS 4, package a new release, and upload it.


## QGIS and QField catalogues

The main menu provides **QGIS Plugins**, **QField Plugins**, and
**Dokumentation**. QGIS keeps its existing `/`, `/plugins.xml`, XML-RPC,
`/upload`, and download URLs. QField has its own `/qfield` catalogue,
`/qfield/upload` form, download URLs and storage subdirectories. QField
plugins are never included in the QGIS XML feed.

Both catalogues use the existing user accounts and roles: superusers and
users with the `upload` role can upload; only superusers can change visibility,
assign roles or delete plugins. Public plugins are visible to everyone;
private plugins require a superuser or a user with an assigned role. These
checks also protect detail pages, icons and ZIP downloads. Updating a package
preserves its visibility and role assignments.

QField application plugin ZIPs must contain `main.qml` at the root. Although
QField itself permits plugins without metadata, this catalogue requires a root
`metadata.txt` with a `[general]` section containing `name`, `version`,
`description`, and `author`. Optional fields include `about`, `email`,
`homepage`, `repository`, `icon`, `tags`, and translated fields such as
`about[de]`. Keep the ZIP filename stable across updates; increase `version`.
QGIS fields such as `qgisMinimumVersion` are not required for QField.
Project-specific QField plugins bundled with `.qgs`/`.qgz` projects are outside
this catalogue's scope.

### Localized metadata and existing installations

Unqualified metadata values (for example `about`) supply the English text;
`about[de]`, `description[de]`, `changelog[de]`, and other localized text fields
supply German text. The detail page offers **Deutsch / English** links and uses
the browser language by default (German when unspecified). Missing translations
fall back to the unqualified value. Text is escaped and multiline formatting is
preserved. QGIS XML metadata retains its existing unqualified values.

Startup adds a `plugin_details` table without changing the existing `plugin`
table. Existing plugins remain QGIS entries. Back up the database and plugin
files before upgrading. Metadata and translations are imported when a plugin
package is uploaded. Upload validation distinguishes missing from duplicate
metadata and reports missing required fields before writing files.

### Documentation handoff



### Tests

```sh
pip install -r requirements-dev.txt
python -m pytest -q
```
