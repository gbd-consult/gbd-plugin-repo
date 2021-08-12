"""End points for Plugins."""
import os
from repo import app, db
from flask import request, Response, render_template, \
    redirect, flash, abort, url_for
from flask_login import login_required, current_user
from repo.helpers import readline_generator, md5, newerVersion
from repo.models import Plugin, Role, User
from lxml import etree
from zipfile import ZipFile
from configparser import ConfigParser
from tempfile import TemporaryDirectory
import shutil
from sqlalchemy import or_


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_plugin():  # FIXME: This is very complex spaghetti code.
    """Upload a zip compressed QGIS plugin."""
    if request.method == 'POST':
        # Check if there is a file part
        if 'file' not in request.files:
            flash('no file part')
            return redirect(url_for('upload_plugin'))
        file = request.files['file']

        # check if the filename is emtpy
        if file.filename == '':
            flash('no selected file')
            return redirect(url_for('upload_plugin'))

        # Check filetype
        if not file.filename.endswith('.zip'):
            flash('wrong filetype')
            return redirect(url_for('upload_plugin'))

        # Create a temp file for our zip
        with TemporaryDirectory() as dir:
            tmp_path = os.path.join(dir, file.filename)
            file.save(tmp_path)
            with open(tmp_path, 'rb') as f:
                # Check if plugin is a duplicate
                existing_plugin = Plugin.query.filter_by(
                    md5_sum=md5(f)).first()
                if existing_plugin:
                    flash('uploaded plugin is a duplicate!')
                    return redirect(url_for('upload_plugin'))

                # Check if we can open the zip file
                try:
                    zf = ZipFile(f)
                except:
                    flash("broken zip file")
                    return redirect(url_for('upload_plugin'))

                # Check if the zip file contains a metadata.txt file
                metadataFiles = list(filter(
                    lambda x: x.endswith('/metadata.txt')
                    or x == 'metadata.txt', zf.namelist()))
                if not len(metadataFiles) == 1:
                    flash("missing metadata.txt")
                    return redirect(url_for('upload_plugin'))

                # Try to read metadata.txt
                try:
                    metadata = zf.open(metadataFiles.pop())
                    config = ConfigParser()
                    config.read_file(readline_generator(metadata))

                    name = config.get('general', 'name')
                    version = config.get('general', 'version')
                    description = config.get('general', 'description')
                    qgis_min_version = config.get('general',
                                                  'qgisMinimumVersion')
                    qgis_max_version = config.get('general',
                                                  'qgisMaximumVersion',
                                                  fallback='3.99')
                    author_name = config.get('general', 'author')
                    repository = config.get('general',
                                            'repository', fallback='')
                    about = config.get('general', 'about', fallback='')

                except:
                    flash("invalid metadata.txt file")
                    return redirect(url_for('upload_plugin'))

                # Check if there already is a plugin with that name
                old_plugin = Plugin.query.filter_by(
                    file_name=file.filename).first()
                if old_plugin and \
                        not newerVersion(version, old_plugin.version):
                    flash(
                        'rejecting upload. \
                        uploaded version of %s is older than existing one'
                        % name)
                    return redirect(url_for('upload_plugin'))

                try:
                    plugin_path = os.path.join(
                        app.config['GBD_PLUGIN_PATH'], file.filename)
                    shutil.move(tmp_path, plugin_path)
                except:
                    flash("copying of new plugin failed")
                    return redirect(url_for('upload_plugin'))

                if old_plugin:
                    plugin = old_plugin
                    app.logger.info('PLUGIN_UPDATED: %s(%s) to %s by user %s'
                                    % (name, plugin.id,
                                       version, current_user.name))
                    msg = 'successfuly updated %s to Version %s' \
                        % (name, version)
                else:
                    plugin = Plugin()
                    app.logger.info('PLUGIN_CREATED: %s by user %s'
                                    % (name, current_user.name))
                    msg = 'successfuly uploaded %s' % name

                plugin.name = name
                plugin.version = version
                plugin.description = description
                plugin.qgis_min_version = qgis_min_version
                plugin.qgis_max_version = qgis_max_version
                plugin.author_name = author_name
                plugin.md5_sum = md5(f)
                plugin.file_name = file.filename
                plugin.user_id = current_user.id
                # optional
                plugin.repository = repository
                plugin.about = about

                db.session.add(plugin)
                db.session.commit()
                flash(msg)

        return redirect(url_for('upload_plugin'))
    else:
        return render_template("upload.html")


@app.route('/plugins/<int:plugin_id>/delete')
@login_required
def delete_plugin(plugin_id):
    """Delete a give plugin."""
    p = Plugin.query.get(plugin_id)
    if not p:
        return abort(404)
    if not (current_user.superuser or current_user.id == p.user_id):
        return abort(401)
    db.session.delete(p)
    db.session.commit()
    os.remove(os.path.join(
        app.config['GBD_PLUGIN_PATH'], p.file_name))
    app.logger.info('PLUGIN_DELETED: %s(%s) by user %s' %
                    (p.name, p.id, current_user.name))
    return redirect(url_for('get_plugins'))


@app.route('/plugins.xml')
@app.route('/')
def get_plugins():
    print(current_user)
    """Generate the 'plugins.xml' and html view from the DB."""
    if current_user.is_anonymous:
        plugins = Plugin.query.filter_by(public=True)
    elif current_user.superuser:
        plugins = Plugin.query.all()
    else:
        print(current_user.id)
        plugins = Plugin.query.join(Plugin.roles, isouter=True).join(Role.users, isouter=True).filter(
                or_( User.id == current_user.id, 
                     Plugin.public == True, 
                     Plugin.user_id == current_user.id)
            ).all()
        print(plugins)

    if request.args.get('qgis'):
        version = request.args.get('qgis')
        print(newerVersion(version, plugins[0].qgis_max_version))
        print(plugins[0].qgis_max_version)
        print(version)
        plugins = [p for p in plugins
                   if not newerVersion(p.qgis_min_version, version) and
                   not newerVersion(version, p.qgis_max_version)]

    if request.path.endswith('plugins.xml'):
        plugin_root = etree.Element('plugins')

        for p in plugins:
            plugin_element = etree.Element(
                'pyqgis_plugin', version=p.version, name=p.name)

            version = etree.SubElement(plugin_element, 'version')
            version.text = p.version
            description = etree.SubElement(plugin_element, 'description')
            description.text = p.description
            author_name = etree.SubElement(plugin_element, 'author_name')
            author_name.text = p.author_name
            file_name = etree.SubElement(plugin_element, 'file_name')
            file_name.text = p.file_name
            download_url = etree.SubElement(plugin_element, 'download_url')
            download_url.text = os.path.join(
                app.config['GBD_PLUGIN_ROOT'], p.file_name)
            qgis_minimum_version = etree.SubElement(
                plugin_element, 'qgis_minimum_version')
            qgis_minimum_version.text = p.qgis_min_version
            qgis_maximum_version = etree.SubElement(
                plugin_element, 'qgis_maximum_version')
            qgis_maximum_version.text = p.qgis_max_version
            md5_sum = etree.SubElement(plugin_element, 'md5_sum')
            md5_sum.text = p.md5_sum

            plugin_root.append(plugin_element)

        return Response(etree.tostring(plugin_root), mimetype='text/xml')
    else:
        roles = Role.query.all()
        return render_template("plugins.html",
                               plugins=plugins, user=current_user, roles=roles)

@app.route('/plugin/<int:plugin_id>/edit', methods=['POST'])
def edit_plugin(plugin_id):
    
    plugin = Plugin.query.filter_by(id=plugin_id).first()

    if not plugin:
        return abort(404)

    if not (current_user.superuser or plugin.user.id == current_user.id):
        return abort(401)

    changed = False
    if current_user.superuser:  # only superuser can assign roles at the moment
        roles = Role.query.all()
        for role in roles:
            should_have_access = request.form.get(f'role_{role.id}') == "on"
            has_access = (role in plugin.roles)
            if has_access and not should_have_access:
                plugin.roles.remove(role)
                changed = True
                app.logger.info( f'PLUGIN_ROLE_REMOVED: {role.name} added to plugin {plugin.name}({plugin.id}) by {current_user.name}')
            elif should_have_access and not has_access:
                app.logger.info( f'PLUGIN_ROLE_ADDED: {role.name} added to plugin {plugin.name}({plugin.id}) by {current_user.name}')
                plugin.roles.append(role)
                changed = True
    
    # uploader and superuser can both set a plugins visibility to public
    should_be_public = (request.form.get('public') == "on")
    if should_be_public and not plugin.public:
        plugin.public = True
        changed = True
        app.logger.info( f'PLUGIN_MADE_PUBLIC: plugin {plugin.name}({plugin.id}) made public by {current_user.name}')
    elif plugin.public and not should_be_public:
        plugin.public = False
        changed = True
        app.logger.info( f'PLUGIN_MADE_PRIVATE: plugin {plugin.name}({plugin.id}) made private by {current_user.name}')

    if changed:
        db.session.add(plugin)
        db.session.commit()
        flash("successfuly changed plugin: %s" % plugin.name)
    else:
        flash("no changes were made")

    return redirect(url_for('get_plugins'))