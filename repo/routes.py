import requests as r
from repo import app
from flask import request
from repo.helpers import extractPluginMetadata

@app.route('/plugin-release', methods = ['POST'])
def pluginRelease():
    if request.method == 'POST':
        data = request.json
        if data['action'] in ['created','published']:
            release_data = data['release']
            if len(release_data['assets']) > 0:
                assets = [a for a in release_data['assets'] if a['content_type'] == 'application/zip']
                asset = assets.pop()
                if asset:
                    response = r.get(asset['browser_download_url'], allow_redirects=True)
                    zip_file = '/tmp/plugin_repo/%s' % asset['name']
                    open(zip_file, 'wb').write(response.content)
                    p = extractPluginMetadata(zip_file, 'http:/fno.rd/')
                    if p.version == release_data['tag_name']:
                        print('fnord')

                    return 'downloaded new plugin release'
    return 'invalid release data'
