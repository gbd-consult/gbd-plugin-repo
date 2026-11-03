# Documentation

The **Dokumentation** menu opens the standalone Dog handbooks at `/doc/`.
Install the repository requirements, then run from the repository root:

```sh
python3 doc/doc.py build    # Build into doc/html/doc
python3 doc/doc.py server   # Live preview: http://localhost:5500/doc/
```

Docker builds the handbooks automatically. Generated HTML is ignored by Git.
`DOCUMENTATION_PATH` overrides the build directory; `DOCUMENTATION_URL`
optionally redirects the menu to an external documentation site.

## Structure

The books follow WebSuite's `konfigurator-de` naming convention:

```text
books/
  index.doc.md
  qgis-plugins-de/index.doc.md
  qgis-geoservices-de/
    index.doc.md
    qgis-geoservices-images/01-karten.png
  qfield-plugins-de/index.doc.md
  qfield-geoservices-de/index.doc.md
```

Each handbook uses `<platform>-<plugin>-<language>` as its directory and root
section ID (SID). Both current handbooks are German (`-de`).

## Add a handbook

1. Create `books/<platform>-<plugin>-<language>/index.doc.md`:

   ```markdown
   # Pluginname :/qgis-pluginname-de

   Describe the plugin here.

   ## Installation :installation

   Installation steps.

   ### Voraussetzungen ::

   This heading stays within the installation chapter.
   ```

2. Add its link and language to the appropriate `qgis-plugins-de` or
   `qfield-plugins-de` index, then embed it with `## :/qgis-pluginname-de`.
   Add a home-page table entry in `books/index.doc.md` if needed.
3. Put images in `<platform>-<plugin>-images/`, using numbered lowercase ASCII
   filenames and descriptive alt text:

   ```markdown
   ![Kartenansicht des Plugins](/qgis-pluginname-images/01-karten.png){border=4}
   ```

   Optimize large images; PNG, SVG and WebP are supported. Dog publishes images
   by filename into `_static`, so different images need globally distinct names.
4. Build and check links, images, navigation and search. The handbook URL is
   `/doc/qgis-pluginname-de/index.html`.

For translations, create a separate book with a suffix such as `-en`, translate
its text and update its SID and chapter links. Register it under the platform
group with its language. Reuse identical images; give translated screenshots
distinct filenames such as `01-maps-en.png`. Publish only existing translations.

## Theme and publishing

- `options.json`: build paths, branding and `fileSplitLevel` (keep `{"/": 3}`).
- `theme/`: standalone layout, sidebar, search and styles.
- `vendor/`: bundled Dog and Jump documentation tools.

Commit Markdown, images, theme and build configuration. Keep generated HTML,
caches and local plugin data out of Git. Plugin ZIP uploads and handbooks are
maintained separately.

[Dog syntax reference](https://docs.gbd-websuite.de/stable/dev-en/documentation/dog/index.html)
