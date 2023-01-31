"""Authentication end points."""
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from repo import app, db, login_manager
from repo.models import Plugin, Role, User


@login_manager.request_loader
def load_user_from_header(request):
    auth = request.authorization
    if not auth:
        # no basic auth provided, continue with normal auth
        return None

    user = User.query.filter_by(name=auth.username).first()
    if not user or not user.check_password(auth.password):
        # wrong basic auth provided deny access
        abort(401)

    # basic auth works
    return user


@login_manager.user_loader
def load_user(user_id):
    """Load a user by id."""
    return User.query.filter_by(id=user_id).first()


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log in the user."""
    if current_user.is_authenticated:
        return redirect(url_for("get_plugins"))
    if request.method == "POST":
        user = User.query.filter_by(name=request.form.get("username")).first()
        if user is None or not user.check_password(request.form.get("password")):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        login_user(user)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("get_plugins")
        return redirect(next_page)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log out the user."""
    logout_user()

    return redirect(url_for("get_plugins"))


@app.route("/users")
@login_required
def get_users():
    """List all users."""
    if not current_user.superuser:
        return abort(401)
    users = User.query.all()
    return render_template("users.html", users=users)


@app.route("/user/add", methods=["GET", "POST"])
@login_required
def add_user():
    """Add a new User to the Database."""
    if not current_user.superuser:
        return abort(401)
    roles = Role.query.all()
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        if name is None or password is None:
            flash("Enter Username and password")
            return redirect(url_for("add_user"))
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            flash("An user with that name already exists")
            return redirect(url_for("add_user"))
        elif len(password) < 8:
            flash("password needs to have at least 8 characters")
            return redirect(url_for("add_user"))
        else:
            if request.form.get("superuser"):
                superuser = True
            else:
                superuser = False
            user = User(name=name, superuser=superuser)
            user.set_password(password)

            for role in roles:
                should_have_role = request.form.get(f"role_{role.id}") == "on"
                if should_have_role:
                    user.roles.append(role)

            db.session.add(user)
            db.session.commit()
            flash(f"successfuly created user: {name}")
            app.logger.info(
                f"USER_CREATED: {user.name}({user.id}) by user {current_user.name}"
            )
            return redirect(url_for("get_users"))
    else:
        return render_template("user.html", roles=roles)


@app.route("/user/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    """Edit a given user."""
    if not current_user.superuser:
        return abort(401)
    else:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return abort(404)
        roles = Role.query.all()

        if request.method == "POST":
            changed = False
            password = request.form.get("password")
            if not (password is None or password == ""):
                if len(password) < 8:
                    flash("password needs to have at least 8 characters")
                    return redirect(url_for("edit_user", user_id=user_id))
                user.set_password(password)
                changed = True
                app.logger.info(
                    f"USER_PASSWORD_CHANGED: changed password for {user.name} by {current_user.name}"
                )
            if request.form.get("superuser") and not user.superuser:
                user.superuser = True
                changed = True
                app.logger.info(
                    f"USER_SUPERUSER_CHANGED: {user.name} promoted to superuser by {current_user.name}"
                )
            if (
                user.superuser
                and request.form.get("superuser") is None
                and user.id != current_user.id
            ):
                user.superuser = False
                changed = True
                app.logger.info(
                    f"USER_SUPERUSER_CHANGED: {user.name} demoted to user by {current_user.name}"
                )

            for role in roles:
                should_have_role = request.form.get(f"role_{role.id}") == "on"
                has_role = role in user.roles
                if should_have_role and not has_role:
                    user.roles.append(role)
                    changed = True
                    app.logger.info(
                        f"USER_ROLE_ADDED: {role.name} added to user {user.name}({user.id}) by {current_user.name}"
                    )
                elif has_role and not should_have_role:
                    user.roles.remove(role)
                    changed = True
                    app.logger.info(
                        f"USER_ROLE_REMOVED: {role.name} added to user {user.name}({user.id}) by {current_user.name}"
                    )

            if changed:
                db.session.add(user)
                db.session.commit()
                flash("successfuly changed user: %s" % user.name)
                return redirect(url_for("get_users"))
            else:
                flash("nothing changed")
                return redirect(url_for("edit_user", user_id=user_id))
        else:
            return render_template("user.html", user=user, roles=roles)


@app.route("/user/<int:user_id>/delete")
@login_required
def delete_user(user_id):
    """Delete a given user."""
    if not current_user.superuser:
        return abort(401)
    else:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return abort(404)
        if user.id == current_user.id:
            flash("can't delete yourself")
            return redirect(url_for("get_users"))
        plugins = Plugin.query.filter_by(user_id=user.id).all()
        for p in plugins:
            p.user_id = current_user.id
        db.session.add_all(plugins)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        flash(f"removed user {user.name}")
        app.logger.info(
            f"USER_REMOVED: {user.name}({user.id}) by user {current_user.name}"
        )
        return redirect(url_for("get_users"))


@app.route("/roles")
@login_required
def get_roles():
    """List all roles."""
    if not current_user.superuser:
        return abort(401)
    roles = Role.query.all()
    return render_template("roles.html", roles=roles)


@app.route("/role/add", methods=["GET", "POST"])
@login_required
def add_role():
    """Add a new role to the database."""
    if not current_user.superuser:
        return abort(401)
    if request.method == "POST":
        name = request.form.get("rolename")
        if name is None:
            flash("Enter name for role")
            return redirect(url_for("add_role"))
        existing_role = Role.query.filter_by(name=name).first()
        if existing_role:
            flash("A role with that name already exists")
            return redirect(url_for("add_role"))
        else:
            role = Role(name=name)
            db.session.add(role)
            db.session.commit()
            flash(f"successfully created role: {name}")
            app.logger.info(
                f"ROLE_CREATED: {role.name}({role.id}) by user {current_user.name}"
            )
            return redirect(url_for("get_roles"))
    else:
        return render_template("role.html")


@app.route("/role/<int:role_id>/edit", methods=["GET", "POST"])
@login_required
def edit_role(role_id):
    """Edit a given role."""
    if not current_user.superuser:
        return abort(401)
    else:
        role = Role.query.filter_by(id=role_id).first()
        if not role:
            return abort(404)
        if request.method == "POST":
            changed = False

            rolename = request.form.get("rolename")
            if rolename and rolename != role.name:
                old = role.name
                role.name = rolename
                changed = True
                app.logger.info(
                    f"ROLE_NAME_CHANGED: {old}({role.id}) renamed to {role.name} by {current_user.name}"
                )
            if changed:
                db.session.add(role)
                db.session.commit()
                flash("successfully changed role")
                return redirect(url_for("get_roles"))
            else:
                flash("nothing changed")
                return redirect(url_for("edit_role", role_id=role_id))
        else:
            return render_template("role.html", role=role)


@app.route("/role/<int:role_id>/delete")
@login_required
def delete_role(role_id):
    if not current_user.superuser:
        return abort(401)
    else:
        role = Role.query.filter_by(id=role_id).first()
        if not role:
            return abort(404)
        # maybe add check to not delete admin role, if superuser ends up not being hardcoded

        db.session.delete(role)
        db.session.commit()
        flash(f"deleted role {role.name}")
        app.logger.info(f"ROLE_REMOVED: {role.name}({role.id}) by {current_user.name}")
        return redirect(url_for("get_roles"))
