from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.project_model import Project

project_bp = Blueprint('project_bp', __name__, url_prefix='/proyectos')

@project_bp.route('/')
def index():
    if 'user_id' not in session:
        flash('Por favor inicia sesión para acceder al dashboard.', 'warning')
        return redirect(url_for('auth_bp.login'))

    proyectos = Project.query.all()
    return render_template('projects/index.html', proyectos=proyectos)

@project_bp.route('/proyecto/<int:id>')
def detalle_proyecto(id):
    proyecto = Project.query.get_or_404(id)
    epics = proyecto.epics  # viene de la relación definida en el modelo
    return render_template('projects/detalle.html', proyecto=proyecto, epics=epics)

@project_bp.route('/proyecto/nuevo', methods=['GET', 'POST'])
def nuevo_proyecto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        nuevo = Project(nombre=nombre, descripcion=descripcion)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('project_bp.index'))
    return render_template('projects/nuevo.html')
