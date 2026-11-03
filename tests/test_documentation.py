"""Verify built handbook navigation, assets and Flask integration together."""

import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import pytest
from lxml import html

from repo import app


@pytest.fixture(scope="module")
def built_docs(tmp_path_factory):
    import sys

    doc_root = Path(__file__).resolve().parents[1] / "doc"
    sys.path.insert(0, str(doc_root / "vendor"))
    from dog.builder import Builder

    options = json.loads((doc_root / "options.json").read_text())
    for key in ["docRoots", "extraAssets"]:
        options[key] = [str(doc_root / value) for value in options[key]]
    options["pageTemplate"] = str(doc_root / options["pageTemplate"])
    output = tmp_path_factory.mktemp("handbooks")
    options["outputDir"] = str(output)
    builder = Builder(options)
    builder.build_html(write=True)
    assert {
        "/",
        "/qgis-geoservices-de",
        "/qfield-geoservices-de",
    } <= builder.sectionMap.keys()
    return output


def test_built_docs_are_available_through_the_documentation_menu(
    client, monkeypatch, built_docs
):
    monkeypatch.setitem(app.config, "DOCUMENTATION_PATH", str(built_docs))
    response = client.get("/documentation", follow_redirects=True)
    assert response.status_code == 200
    assert b"GBD" in response.data and b"QField Plugins" in response.data
    assert b"QGIS Plugins" in response.data
    manual = client.get("/doc/qgis-geoservices-de/index.html")
    assert manual.status_code == 200
    assert b"GeoServices" in manual.data
    chapters = html.fromstring(manual.data).xpath(
        '//div[@class="md-local-toc"]//a/@href'
    )
    assert len(chapters) == 13
    assert all(client.get(url).status_code == 200 for url in chapters)
    mobile_manual = client.get("/doc/qfield-geoservices-de/index.html")
    assert mobile_manual.status_code == 200
    mobile_chapters = html.fromstring(mobile_manual.data).xpath(
        '//div[@class="md-local-toc"]//a/@href'
    )
    assert len(mobile_chapters) == 12
    assert all(client.get(url).status_code == 200 for url in mobile_chapters)


def test_every_generated_link_anchor_and_image_resolves(built_docs):
    images = set()
    pages = list(built_docs.rglob("*.html"))
    assert len(pages) >= 30
    for page in pages:
        tree = html.fromstring(page.read_bytes())
        base = "/doc/" + page.relative_to(built_docs).as_posix()
        for image in tree.xpath("//img"):
            assert image.get("alt"), f"Missing image alt text: {page}"
            images.add(image.get("src"))
        for target in tree.xpath(
            "//a/@href | //img/@src | //script/@src | //link/@href"
        ):
            url = urlsplit(urljoin(base, target))
            if url.netloc or not url.path.startswith("/doc/"):
                continue
            path = built_docs / unquote(url.path.removeprefix("/doc/"))
            assert path.is_file(), f"Broken link in {page}: {target}"
            if url.fragment and path.suffix == ".html":
                target_tree = html.fromstring(path.read_bytes())
                assert unquote(url.fragment) in target_tree.xpath(
                    "//*[@id]/@id"
                ), target
    assert len(images) == 12  # Eleven QGIS screenshots and the documentation logo.


@pytest.mark.parametrize("platform", ["qgis", "qfield"])
def test_previous_handbook_links_redirect_to_language_book(
    client, monkeypatch, built_docs, platform
):
    monkeypatch.setitem(app.config, "DOCUMENTATION_PATH", str(built_docs))
    for page in ["index.html", "status/index.html"]:
        response = client.get(f"/doc/{platform}/geoservices/{page}")
        assert response.status_code == 301
        assert response.location == f"/doc/{platform}-geoservices-de/{page}"
        assert client.get(response.location).status_code == 200


def test_documentation_uses_its_standalone_layout_for_all_visitors(
    client, monkeypatch, built_docs, login
):
    monkeypatch.setitem(app.config, "DOCUMENTATION_PATH", str(built_docs))

    for authenticated in [False, True]:
        if authenticated:
            login()
        response = client.get("/doc/")
        assert response.status_code == 200
        assert response.data == (built_docs / "index.html").read_bytes()
        document = html.fromstring(response.data)
        assert len(document.xpath('//header[@class="repository-header"]')) == 1
        assert not document.xpath('//nav[contains(@class,"navbar")]')
        assert not document.xpath('//link[contains(@href,"gpr.css")]')
        assert not document.xpath('//a[@href="/users"] | //form[@action="/logout"]')


def test_generated_handbook_is_served_verbatim_without_jinja_evaluation(
    client, monkeypatch, tmp_path
):
    monkeypatch.setitem(app.config, "DOCUMENTATION_PATH", str(tmp_path))
    (tmp_path / "index.html").write_text(
        "<html><head><title>Handbuch</title></head><body>"
        '<div id="handbook">{{ config.SECRET_KEY }}</div></body></html>'
    )
    response = client.get("/doc/")
    assert response.status_code == 200
    assert response.data == (tmp_path / "index.html").read_bytes()
    assert b"{{ config.SECRET_KEY }}" in response.data
    assert b"test-secret-key" not in response.data


def test_navigation_and_search_indexes_are_served(client, monkeypatch, built_docs):
    monkeypatch.setitem(app.config, "DOCUMENTATION_PATH", str(built_docs))
    for filename in ["_toc.json", "_index.json", "_index.bin", "theme.js", "theme.css"]:
        assert client.get("/doc/_static/" + filename).status_code == 200
    toc = client.get("/doc/_static/_toc.json").get_json()
    sections = {section["sid"]: section for section in toc["sections"]}
    for platform, label in [("qgis", "QGIS"), ("qfield", "QField")]:
        group = sections[f"/{platform}-plugins-de"]
        manual = sections[f"/{platform}-geoservices-de"]
        assert group["title"] == f"GBD {label}-Plugins"
        assert manual["title"] == "GeoServices"
        assert manual["parent"] == group["nid"]
    assert any(
        section["sid"] == "/qgis-geoservices-de/status" for section in toc["sections"]
    )


def test_documentation_cannot_serve_source_files_or_escape_build_directory(
    client, monkeypatch, built_docs
):
    monkeypatch.setitem(app.config, "DOCUMENTATION_PATH", str(built_docs))
    for url in [
        "/doc/../options.json",
        "/doc/%2e%2e/README.md",
        "/doc/content/qgis-geoservices-de/index.doc.md",
    ]:
        assert client.get(url).status_code == 404
