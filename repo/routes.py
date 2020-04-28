import os
from repo import app, db, auth
from flask import request, Response, render_template, redirect, flash
from repo.helpers import readline_generator, md5, newerVersion
from repo.models import Plugin
from lxml import etree
from zipfile import ZipFile
from configparser import ConfigParser
from tempfile import TemporaryDirectory
import shutil

@app.route('/upload', methods=['GET','POST'])
@auth.login_required
def uploadPlugin():
    """ Upload a zip compressed QGIS plugin """
    if request.method == 'POST':
        # Check if there is a file part
        if 'file' not in request.files:
            flash('no file part')
            return redirect(request.url)
        file = request.files['file']

        # check if the filename is emtpy
        if file.filename == '':
            flash('no selected file')
            return redirect(request.url)

        # Check filetype
        if not file.filename.endswith('.zip'):
            flash('wrong filetype')
            return(redirect(request.url))

        # Create a temp file for our zip
        with TemporaryDirectory() as dir:
            tmp_path = os.path.join(dir, file.filename)
            file.save(tmp_path)
            with open(tmp_path, 'rb') as f:
                # Check if plugin is a duplicate
                existing_plugin = Plugin.query.filter_by(md5_sum = md5(f)).first()
                if existing_plugin:
                    flash('uploaded plugin is a duplicate!')
                    return(redirect(request.url))

                # Check if we can open the zip file
                try:
                    zf = ZipFile(f)
                except:
                    flash("broken zip file")
                    return(redirect(request.url))

                # Check if the zip file contains a metadata.txt file
                metadataFiles = list(filter(lambda x: x.endswith('/metadata.txt') or x == 'metadata.txt',
                    zf.namelist()))
                if not len(metadataFiles) == 1:
                    flash("missing metadata.txt")
                    return(redirect(request.url))

                # Try to read metadata.txt
                try:
                    metadata = zf.open(metadataFiles.pop())
                    config = ConfigParser()
                    config.read_file(readline_generator(metadata))

                    name = config.get('general', 'name')
                    version = config.get('general', 'version')
                    description = config.get('general', 'description')
                    qgis_min_version = config.get('general', 'qgisMinimumVersion')
                    qgis_max_version = config.get('general', 'qgisMaximumVersion')
                    author_name = config.get('general', 'author')
                    repository = config.get('general', 'repository', fallback = '')
                    about = config.get('general', 'about', fallback = '')

                except:
                    flash("invalid metadata.txt file")
                    return(redirect(request.url))

                # Check if there already is a plugin with that name
                old_plugin = Plugin.query.filter_by(file_name = file.filename).first()
                if old_plugin and not newerVersion(version, old_plugin.version):
                    flash('rejecting upload. uploaded version of %s is older than existing one' % name)
                    return(redirect(request.url))

                try:
                    plugin_path = os.path.join(app.config['PLUGIN_PATH'], file.filename)
                    shutil.move(tmp_path, plugin_path)
                except:
                    flash("copying of new plugin failed")
                    return(redirect(request.url))


                if old_plugin:
                    plugin = old_plugin
                    msg = 'successfuly updated %s to Version %s' % (name,version)
                else:
                    plugin = Plugin()
                    msg = 'successfuly uploaded %s' % name


                plugin.name = name
                plugin.version = version
                plugin.description = description
                plugin.qgis_min_version= qgis_min_version
                plugin.qgis_max_version= qgis_max_version
                plugin.author_name = author_name
                plugin.md5_sum = md5(f)
                plugin.file_name = file.filename
                # optional
                plugin.repository = repository
                plugin.about = about

                db.session.add(plugin)
                db.session.commit()
                flash(msg)

        return(redirect(request.url))
    else:
        return(render_template("upload.html", user = auth.username()))



@app.route('/plugins.xml')
@app.route('/')
def getPlugins():
    """ Generates the 'plugins.xml' and html view from the DB. """
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

    if request.path.endswith('plugins.xml'):
        return Response(etree.tostring(pluginRoot), mimetype='text/xml')
    else:
        return render_template("plugins.html", plugins = plugins)
