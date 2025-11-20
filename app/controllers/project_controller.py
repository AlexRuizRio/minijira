from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.project_model import Project
from app.models.epic_hu_model import TipoEnum

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
    
    # 🔹 Todas las filas relacionadas con el proyecto
    todas = proyecto.epics  # SQLAlchemy ya carga solo los que tienen project_id = proyecto.id

    # 🔹 Filtrar solo épicas
    epicas = [e for e in todas if e.tipo == TipoEnum.EPIC]

    # 🔹 Filtrar HUs hijas de cada épica y que pertenezcan al mismo proyecto
    epics_con_hus = []
    for epic in epicas:
        hu_filtradas = [hu for hu in todas if hu.tipo == TipoEnum.HU and hu.epica_id == epic.id]
        # Añadimos como tupla o diccionario temporal para la vista
        epics_con_hus.append({'epic': epic, 'hus': hu_filtradas})

    # 🔹 HUs sueltas (sin épica)
    hus_sueltas = [hu for hu in todas if hu.tipo == TipoEnum.HU and hu.epica_id is None]

    return render_template(
        'projects/detalle.html',
        proyecto=proyecto,
        epics_con_hus=epics_con_hus,
        hus_sueltas=hus_sueltas
    )   


@project_bp.route('/proyecto/nuevo', methods=['GET', 'POST'])
def nuevo_proyecto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        user_id = session.get('user_id')
        nuevo = Project(nombre=nombre, descripcion=descripcion, user_created=user_id)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('project_bp.index'))
    return render_template('projects/nuevo.html')

@project_bp.route('/proyecto/<int:id>/editar', methods=['GET', 'POST'])
def editar_proyecto(id):
    proyecto = Project.query.get_or_404(id)

    if request.method == 'POST':
        proyecto.nombre = request.form['nombre']
        proyecto.descripcion = request.form['descripcion']
        db.session.commit()
        return redirect(url_for('project_bp.detalle_proyecto', id=id))

    return render_template('projects/editar.html', proyecto=proyecto)


@project_bp.route('/proyecto/<int:id>/eliminar')
def eliminar_proyecto(id):
    proyecto = Project.query.get_or_404(id)
    db.session.delete(proyecto)
    db.session.commit()
    return redirect(url_for('project_bp.index'))
