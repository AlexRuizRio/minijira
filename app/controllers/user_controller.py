from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.user_model import User, Role
from app.utils.decorators import role_required

user_bp = Blueprint('user_bp', __name__, url_prefix='/usuarios')
URL_INDEX = 'user_bp.index'

@user_bp.route('/')
@role_required('admin')
def index():
    usuarios = User.query.all()
    roles = Role.query.all()
    return render_template('users/index.html', usuarios=usuarios, roles=roles)


@user_bp.route('/nuevo', methods=['GET', 'POST'])
@role_required('admin')
def nuevo_usuario():
    roles = Role.query.all()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        selected_roles = request.form.getlist('roles')  # <- cambia aquí

        user = User(username=username, email=email)
        user.set_password(password)

        for role_id in selected_roles:
            rol = Role.query.get(role_id)
            if rol:
                user.roles.append(rol)

        db.session.add(user)
        db.session.commit()
        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for(URL_INDEX))

    return render_template('users/nuevo.html', roles=roles)


@user_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@role_required('admin')
def editar_usuario(id):
    user = User.query.get_or_404(id)
    roles = Role.query.all()
    if user.username != 'admin':
        if request.method == 'POST':
            user.username = request.form['username']
            user.email = request.form['email']

            selected_roles = request.form.getlist('roles')

            # Actualizar roles: limpiar y volver a asignar
            user.roles.clear()
            for role_id in selected_roles:
                rol = Role.query.get(role_id)
                if rol:
                    user.roles.append(rol)

            db.session.commit()
            flash('Usuario actualizado correctamente.', 'success')
            return redirect(url_for(URL_INDEX))
    else:
            flash(f'Usuario {user.username} no puede ser editado', 'danger')
            return redirect(url_for(URL_INDEX))
    return render_template('users/editar.html', user=user, roles=roles)


@user_bp.route('/usuario/delete/<int:id>', methods=['POST'])
@role_required('admin')
def delete_usuario(id):
    usuario = User.query.get_or_404(id)
    if usuario.username != 'admin':
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuario {usuario.username} eliminado correctamente.', 'success')
        return redirect(url_for(URL_INDEX))
    else:
        flash(f'Usuario {usuario.username} no puede ser eliminado', 'danger')
        return redirect(url_for(URL_INDEX))


############ ROLES ############


@user_bp.route('/roles/nuevo', methods=['GET', 'POST'])
@role_required('admin')
def nuevo_rol():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        rol = Role(nombre=nombre, descripcion=descripcion)
        db.session.add(rol)
        db.session.commit()
        flash('Rol creado correctamente.', 'success')
        return redirect(url_for(URL_INDEX))

    return render_template('users/nuevo_rol.html')


@user_bp.route('/editar_rol/<int:id>', methods=['GET', 'POST'])
@role_required('admin')
def editar_rol(id):
    rol = Role.query.get_or_404(id)
    if rol.nombre == 'admin':
        flash('No se puede editar el rol admin', 'danger')
        return redirect(url_for(URL_INDEX))
    if request.method == 'POST':
        rol.nombre = request.form['nombre']
        rol.descripcion = request.form['descripcion']
        db.session.commit()
        flash(f'Rol "{rol.nombre}" actualizado correctamente.', 'success')
        return redirect(url_for(URL_INDEX))

    return render_template('users/editar_rol.html', rol=rol)


@user_bp.route('/delete_rol/<int:id>', methods=['POST'])
@role_required('admin')
def delete_rol(id):
    rol = Role.query.get_or_404(id)
    if rol.nombre == 'admin':
        flash('No se puede eliminar el rol admin', 'danger')
        return redirect(url_for(URL_INDEX))
    if rol.usuarios:
        flash('No se puede eliminar un rol asignado a usuarios.', 'danger')
        return redirect(url_for(URL_INDEX))

    db.session.delete(rol)
    db.session.commit()
    flash(f'Rol "{rol.nombre}" eliminado correctamente.', 'info')
    return redirect(url_for(URL_INDEX))