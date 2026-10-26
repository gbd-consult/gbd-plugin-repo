# Documentation

## Quick start

Run from the repository root. The `pluginrepo` image already contains the Python requirements; the repository is mounted into the container.

```
docker build -t pluginrepo .
```

Dev server with live reload, at http://localhost:5500/doc/:

```
docker run --rm -it -p 5500:5500 -v "$PWD":/src pluginrepo python3 /src/doc/doc.py server
```

Build static HTML into `doc/html/doc`:

```
docker run --rm -v "$PWD":/src pluginrepo python3 /src/doc/doc.py build
```

Without Docker: `pip install -r requirements.txt`, then `python3 doc/doc.py server` or `python3 doc/doc.py build`.

## Dog

The docs are written in Markdown for Dog, the documentation generator in `vendor/dog`. Dog adds section IDs, section embedding and template commands. See https://docs.gbd-websuite.de/stable/dev-en/documentation/dog/index.html for details.

In short:

- the structure comes from headings, not from file names or folders
- `# Title :/some/sid` gives a section an explicit ID
- a heading that consists only of an ID, `## :/some/sid`, embeds that section
- a section that is not reachable from the root `/` is dropped, with a warning

## Documentation root

Write the docs in `content/`, as `*.doc.md` files. Images (`*.svg`, `*.png`) next to them are copied to the output.

The first top-level heading without an ID becomes the root section `/`. With several files, give the root an explicit `:/` and embed the other files' sections from it.

## Customizing: options.json

`doc.py` reads `options.json` from this folder; relative paths are resolved against it. The options used most often:

| option | meaning |
|---|---|
| `title`, `subTitle` | shown in the sidebar header and the page title |
| `brandName`, `brandLogo`, `brandFooter` | sidebar logo and footer; the logo must be listed in `extraAssets` |
| `docRoots` | folders scanned for docs and images (`content`) |
| `outputDir` | build output (`html/doc`, ignored by git) |
| `webRoot` | URL prefix of all pages, e.g. `/doc` |
| `fileSplitLevel` | how sections are split into HTML files, e.g. `{"/": 3}` |
| `pageTemplate` | page template |
| `extraAssets` | files copied to `_static` (CSS, JS, images) |
| `serverHost`, `serverPort` | dev server address |

All options are described in the Dog documentation. Any additional key, like `brandName`, is available in the page template as `options.<key>`.

## Customizing: page template

- `theme/page.cx.html` is the page layout, written in Jump template syntax (`<% expr %>`, `%if`, `%for`). It receives `options`, `main` (the rendered page content), `breadcrumbs`, `home` and `args` (`pageTemplateArgs` from `options.json`).
- `theme/theme.css` contains the styles. Colors are CSS variables in `:root` at the top of the file.
- `theme/theme.js` handles the sidebar, TOC, search and page navigation, using the element IDs in the template. Keep these IDs when you change the layout.

New files for the theme must be added to `extraAssets`, and are then referenced as `<% options.webRoot %>/_static/<name>`.
