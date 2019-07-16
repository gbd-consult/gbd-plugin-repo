import os
import requests as r
from repo import app, db
from flask import request, abort, Response
from repo.helpers import extractPluginMetadata
from repo.models import Plugin
from lxml import etree

@app.route('/plugin-release', methods = ['POST'])
def pluginRelease():
    if request.method == 'POST':
        data = request.json
        if data['action'] in ['created','published','edited']:
            release_data = data['release']
            if len(release_data['assets']) > 0:
                assets = [a for a in release_data['assets'] if a['content_type'] == 'application/zip']
                asset = assets.pop()
                if asset:
                    response = r.get(asset['browser_download_url'], allow_redirects=True)
                    zip_file = os.path.join(app.config['PLUGIN_PATH'], asset['name'])
                    open(zip_file, 'wb').write(response.content)
                    try:
                        p = extractPluginMetadata(zip_file, 'http:/fno.rd/')
                    except:
                        abort(400)
                    if p.version == release_data['tag_name']:
                        db.session.add(p)
                        db.session.commit()
                        return 'downloaded new plugin release'
                    else:
                        os.remove(zip_file)
        abort(400)
    else:
        abort(405)


@app.route('/plugins.xml', methods = ['GET'])
def getPlugins():
    """ Generates the 'plugins.xml' from the DB. """
    if request.args.get('qgis'):
        version = request.args.get('qgis')
        plugins = Plugin.query.filter(Plugin.qgis_min_version <= version, Plugin.qgis_max_version >= version).all()
    else:
        plugins = Plugin.query.all()

    pluginRoot = etree.Element('plugins')
    for p in plugins:
        pluginElement = etree.Element('pyqgis_plugin', version = p.version, name = p.name)

        version = etree.SubElement(pluginElement, 'version')
        version.text = p.version
        description = etree.SubElement(pluginElement, 'description')
        description.text = p.description
        author_name = etree.SubElement(pluginElement, 'author_name')
        author_name.text = p.author_name
        file_name = etree.SubElement(pluginElement, 'file_name')
        file_name.text = p.file_name
        download_url = etree.SubElement(pluginElement, 'download_url')
        download_url.text = os.path.join(app.config['REPO_ROOT'], p.file_name)
        qgis_minimum_version = etree.SubElement(pluginElement, 'qgis_minimum_version')
        qgis_minimum_version.text = p.qgis_min_version
        qgis_maximum_version = etree.SubElement(pluginElement, 'qgis_maximum_version')
        qgis_maximum_version.text = p.qgis_max_version
        md5_sum = etree.SubElement(pluginElement, 'md5_sum')
        md5_sum.text = p.md5_sum

        pluginRoot.append(pluginElement)
    return Response(etree.tostring(pluginRoot), mimetype='text/xml')
