"""Authentication end points."""
from repo.models import User, Plugin, Role
from repo import login_manager, app, db
from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, request, flash, render_template, abort, current_app, session
from werkzeug.urls import url_parse
from flask_principal import identity_changed, Identity, AnonymousIdentity, identity_loaded, RoleNeed, UserNeed

@login_manager.user_loader
def load_user(user_id):
    """Load a user by id."""
    return User.query.filter_by(id=user_id).first()


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user

    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
    
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in the user."""
    if current_user.is_authenticated:
        return redirect(url_for('get_plugins'))
    if request.method == 'POST':
        user = User.query.filter_by(name=request.form.get('username')).first()
        if user is None or \
                not user.check_password(request.form.get('password')):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user)
        identity_changed.send(current_app._get_current_object(), 
                                identity=Identity(user.id))

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for('get_plugins')
        return redirect(next_page)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    """Log out the user."""
    logout_user()

    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send(current_app._get_current_object(),
                        identity=AnonymousIdentity())

    return redirect(url_for('get_plugins'))


@app.route('/users')
@login_required
def get_users():
    """List all users."""
    if not current_user.superuser:
        return abort(401)
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """Add a new User to the Database."""
    if not current_user.superuser:
        return abort(401)
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        if name is None or password is None:
            flash("Enter Username and password")
            return redirect(url_for('add_user'))
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            flash("An user with that name already exists")
            return redirect(url_for('add_user'))
        elif len(password) < 8:
            flash("password needs to have at least 8 characters")
            return redirect(url_for('add_user'))
        else:
            if request.form.get('superuser'):
                superuser = True
            else:
                superuser = False
            user = User(
                name=name,
                superuser=superuser)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("successfuly created user: %s" % name)
            app.logger.info('USER_CREATED: %s(%s) by user %s'
                            % (user.name, user.id, current_user.name))
            return redirect(url_for('get_users'))
    else:
        return render_template('user.html')


@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit a given user."""
    if not current_user.superuser:
        return abort(401)
    else:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return abort(404)
        if request.method == 'POST':
            changed = False
            password = request.form.get('password')
            if not (password is None or password == ''):
                if len(password) < 8:
                    flash("password needs to have at least 8 characters")
                    return redirect(url_for('edit_user', user_id=user_id))
                user.set_password(password)
                changed = True
                app.logger.info(
                    'USER_PASSWORD_CHANGED: changed password for %s by %s'
                    % (user.name, current_user.name))
            if request.form.get('superuser') and not user.superuser:
                user.superuser = True
                changed = True
                app.logger.info(
                    'USER_SUPERUSER_CHANGED: %s promoted to superuser by %s'
                    % (user.name, current_user.name))
            if user.superuser and request.form.get('superuser') is None \
                    and user.id != current_user.id:
                user.superuser = False
                changed = True
                app.logger.info(
                    'USER_SUPERUSER_CHANGED: %s demoted to user by %s'
                    % (user.name, current_user.name))
            if changed:
                db.session.add(user)
                db.session.commit()
                flash("successfuly changed user: %s" % user.name)
                return redirect(url_for('get_users'))
            else:
                flash("nothing changed")
                return redirect(url_for('edit_user', user_id=user_id))
        else:
            return render_template('user.html', user=user)


@app.route('/user/<int:user_id>/delete')
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
            return redirect(url_for('get_users'))
        plugins = Plugin.query.filter_by(user_id=user.id).all()
        for p in plugins:
            p.user_id = current_user.id
        db.session.add_all(plugins)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        flash("removed user %s" % user.name)
        app.logger.info('USER_REMOVED: %s(%s) by user %s'
                        % (user.name, user.id, current_user.name))
        return redirect(url_for('get_users'))

@app.route('/roles')
@login_required
def get_roles():
    """List all roles."""
    if not current_user.superuser:
        return abort(401)
    roles = Role.query.all()
    return render_template('roles.html', roles=roles)


@app.route('/role/add', methods=['GET', 'POST'])
@login_required
def add_role():
    """Add a new role to the database."""
    if not current_user.superuser:
        return abort(401)
    if request.method == 'POST':
        name = request.form.get('rolename')
        if name is None:
            flash("Enter name for role")
            return redirect(url_for('add_role'))
        existing_role = Role.query.filter_by(name=name).first()
        if existing_role:
            flash("A role with that name already exists")
            return redirect(url_for('add_role'))
        else:
            role = Role(name=name)
            db.session.add(role)
            db.session.commit()
            flash("successfully created role: %s" % name)
            app.logger.info('ROLE_CREATED: %s(%s) by user %s'
                            % (role.name, role.id, current_user.name))
            return redirect(url_for('get_roles'))
    else:
        return render_template('role.html')


@app.route('/role/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(role_id):
    """Edit a given role."""
    if not current_user.superuser:
        return abort(401)
    else:
        role = Role.query.filter_by(id=role_id).first()
        if not role:
            return abort(404)
        if request.method == 'POST':
            changed = False

            rolename = request.form.get('rolename')
            if rolename and rolename != role.name:
                old = role.name
                role.name = rolename
                changed = True
                app.logger.info('ROLE_NAME_CHANGED: %s(%s) renamed to %s by %s' %
                                    (old, role.id, role.name, current_user.name))
            if changed:
                db.session.add(role)
                db.session.commit()
                flash("successfully changed role")
                return redirect(url_for('get_roles'))
            else:
                flash("nothing changed")
                return redirect(url_for('edit_role', role_id=role_id))
        else:
            return render_template('role.html', role=role)


@app.route('/role/<int:role_id>/delete')
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
        flash("deleted role %s" % role.name)
        app.logger.info('ROLE_REMOVED: %s(%s) by user %s' % 
                        (role.name, role.id, current_user.name))
        return redirect(url_for('get_roles'))