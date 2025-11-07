from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user_model import User
from app import db

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username

            if user.roles:
                session['roles'] = [r.nombre for r in user.roles]
            else:
                session['roles'] = ['viewer']

            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('project_bp.index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth_bp.login'))
