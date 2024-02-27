"""End points for Plugins."""
import io
from pathlib import Path

from flask import (Response, abort, flash, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_login import current_user, login_required
from lxml import etree
from packaging import version
from sqlalchemy import or_

from repo import app, db, rpc_handler
from repo.models import Plugin, Role, User
from repo.rpc import RPCError
from repo.upload import plugin_upload

plugin_ns = rpc_handler.namespace("plugin")


@plugin_ns.register
def upload(package):
    """XML RPC function to upload a QGIS plugin."""
    if not current_user.superuser:
        raise RPCError("user not authorized to upload plugins!")

    package_file = io.BytesIO(package.data)
    success, result = plugin_upload(current_user, package_file)

    if success:
        return result
    else:
        raise RPCError(result)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_plugin():
    """Upload a zip compressed QGIS plugin."""
    if not current_user.superuser:
        abort(403)
    if request.method == "POST":
        # Check if there is a file part
        if "file" not in request.files:
            flash("no file part")
            app.logger.info(request.files)
            return redirect(url_for("upload_plugin"))
        file = request.files["file"]

        # check if the filename is emtpy
        if file.filename == "":
            flash("no selected file")
            return redirect(url_for("upload_plugin"))

        # Check filetype
        if not file.filename.endswith(".zip"):
            flash("wrong filetype")
            return redirect(url_for("upload_plugin"))

        package_file = io.BytesIO(file.read())
        success, result = plugin_upload(current_user, package_file)

        if success:
            flash(f"uploaded {file.filename}")
        else:
            flash(result)
        return redirect(url_for("upload_plugin"))
    else:
        return render_template("upload.html")


@app.route("/plugins/<int:plugin_id>/delete")
@login_required
def delete_plugin(plugin_id):
    """Delete a give plugin."""
    if not (current_user.superuser):
        return abort(403)
    p = Plugin.query.get(plugin_id)
    if not p:
        return abort(404)
    db.session.delete(p)
    db.session.commit()
    full_path = (
        Path(app.root_path) / Path(app.config["GBD_PLUGIN_PATH"])
        / Path(p.file_name)
    )
    full_path.unlink()
    app.logger.info(
        f"PLUGIN_DELETED: {p.name}({p.id}) by user {current_user.name}")
    return redirect(url_for("get_plugins"))


@app.route("/plugins.xml")
@app.route("/")
def get_plugins():
    """Generate the 'plugins.xml' and html view from the DB."""
    if current_user.is_anonymous:
        plugins = Plugin.query.filter_by(public=True).all()
    elif current_user.superuser:
        plugins = Plugin.query.all()
    else:
        plugins = (
            Plugin.query.join(Plugin.roles, isouter=True)
            .join(Role.users, isouter=True)
            .filter(
                or_(
                    User.id == current_user.id,
                    Plugin.public,
                )
            )
            .all()
        )

    if request.args.get("qgis"):
        version_arg = request.args.get("qgis")
        plugins = [
            p
            for p in plugins
            if version.parse(
                p.qgisminimumversion) <= version.parse(version_arg)
            and version.parse(
                p.qgismaximumversion) >= version.parse(version_arg)
        ]

    if request.path.endswith("plugins.xml"):
        plugin_root = etree.Element("plugins")

        for p in plugins:
            plugin_root.append(p.to_xml())

        return Response(etree.tostring(plugin_root), mimetype="text/xml")
    else:
        roles = Role.query.all()
        return render_template(
            "plugins.html", plugins=plugins, user=current_user, roles=roles
        )


@app.route("/plugin/<int:plugin_id>")
def get_plugin(plugin_id):
    plugin = Plugin.query.get(plugin_id)
    roles = Role.query.all()
    if plugin:
        if plugin.has_access(current_user):
            return render_template(
                "plugin.html", plugin=plugin, user=current_user, roles=roles
            )
        else:
            abort(403)
    abort(404)


@app.route("/plugin/<int:plugin_id>/edit", methods=["POST"])
@login_required
def edit_plugin(plugin_id):
    plugin = Plugin.query.filter_by(id=plugin_id).first()

    if not plugin:
        return abort(404)

    if not current_user.superuser:
        return abort(403)

    changed = False
    roles = Role.query.all()
    for role in roles:
        should_have_access = request.form.get(f"role_{role.id}") == "on"
        has_access = role in plugin.roles
        if has_access and not should_have_access:
            plugin.roles.remove(role)
            changed = True
            app.logger.info(
                (
                    f"PLUGIN_ROLE_REMOVED: {role.name} lost access tow  "
                    f"plugin {plugin.name}({plugin.id}) by {current_user.name}"
                )
            )
        elif should_have_access and not has_access:
            app.logger.info(
                (
                    f"PLUGIN_ROLE_ADDED: {role.name} gained access to "
                    f"plugin {plugin.name}({plugin.id}) by {current_user.name}"
                )
            )
            plugin.roles.append(role)
            changed = True

    # uploader and superuser can both set a plugins visibility to public
    should_be_public = request.form.get("public") == "on"
    if should_be_public and not plugin.public:
        plugin.public = True
        changed = True
        app.logger.info(
            (
                f"PLUGIN_MADE_PUBLIC: plugin {plugin.name}({plugin.id}) "
                f"made public by {current_user.name}"
            )
        )
    elif plugin.public and not should_be_public:
        plugin.public = False
        changed = True
        app.logger.info(
            (
                f"PLUGIN_MADE_PRIVATE: plugin {plugin.name}({plugin.id}) "
                f"made private by {current_user.name}"
            )
        )

    if changed:
        db.session.add(plugin)
        db.session.commit()
        flash(f"successfuly changed plugin: {plugin.name}")
    else:
        flash("no changes were made")

    return redirect(url_for("get_plugin", plugin_id=plugin.id))


@app.route("/download/<string:filename>")
def download_plugin(filename):
    plugin = Plugin.query.filter(Plugin.file_name == filename).first()
    full_path = Path(app.root_path) / app.config["GBD_PLUGIN_PATH"]

    if plugin:
        if plugin.has_access(current_user):
            plugin.downloads += 1
            db.session.add(plugin)
            db.session.commit()
            return send_from_directory(full_path, plugin.file_name)
        else:
            abort(403)
    abort(404)


@app.route("/icons/<string:filename>")
def get_icon(filename):
    plugin = Plugin.query.filter(Plugin.icon == request.path).first()
    if plugin:
        if plugin.has_access(current_user):
            full_path = Path(app.root_path) / app.config["GBD_ICON_PATH"]
            return send_from_directory(full_path, filename)
        else:
            abort(403)
    abort(404)
