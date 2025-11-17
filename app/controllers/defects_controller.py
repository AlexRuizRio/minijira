from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.defect_model import Defect
from app.models.testcase_model import TestCase
from app.models.result_model import Result
from app.models.user_model import User
from app.utils.decorators import role_required

defects_bp = Blueprint('defects_bp', __name__, url_prefix='/defects')


@defects_bp.route('/')
@role_required('admin', 'miembro', redirect_to='project_bp.index')
def index():
    user_roles = session.get('roles', [])
    user_id = session.get('user_id')

    if 'admin' in user_roles:
        defects = Defect.query.all()
    else:
        defects = Defect.query.filter_by(assigned_to_id=user_id).all()

    return render_template('defects/index.html', defects=defects)


@defects_bp.route('/create', defaults={'result_id': None}, methods=['GET', 'POST'])
@defects_bp.route('/create/<int:result_id>', methods=['GET', 'POST'])
@role_required('admin', 'miembro')
def create(result_id):
    result = Result.query.get(result_id) if result_id else None

    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form.get('descripcion')
        prioridad = request.form.get('prioridad', 'Media')
        assigned_to = request.form.get('assigned_to')
        test_case_id = request.form.get('test_case_id') or (result.test_case_id if result else None)

        nuevo_defect = Defect(
            test_case_id=test_case_id,
            result_id=result.id if result else None,
            titulo=titulo,
            descripcion=descripcion,
            prioridad=prioridad,
            assigned_to_id=int(assigned_to) if assigned_to else None
        )
        db.session.add(nuevo_defect)
        db.session.commit()
        flash("Defecto creado correctamente.", "success")
        return redirect(url_for('defects_bp.index'))

    usuarios = User.query.all()
    test_cases = TestCase.query.all()
    return render_template('defects/create.html', result=result, usuarios=usuarios, test_cases=test_cases)



@defects_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin', 'miembro')
def edit(id):
    defect = Defect.query.get_or_404(id)
    usuarios = User.query.all()
    user_roles = session.get('roles', [])
    user_id = session.get('user_id')

    if request.method == 'POST':
        # permisos: admin o usuario asignado
        if 'admin' in user_roles or defect.assigned_to_id == user_id:
            defect.titulo = request.form['titulo']
            defect.descripcion = request.form['descripcion']
            defect.estado = request.form['estado']
            defect.prioridad = request.form['prioridad']
            assigned_to = request.form.get('assigned_to')
            defect.assigned_to_id = int(assigned_to) if assigned_to else None

            # Si el defecto NO está ligado a TestCase/Result, permitimos cambiar verificado manualmente
            if not defect.test_case_id and not defect.result_id:
                defect.verificado = True if request.form.get('verificado') else False
            else:
                # Si está ligado, forzamos verificado = False al cerrarlo (se gestionará al crear Result pasados)
                if defect.estado.lower() == "cerrado":
                    defect.verificado = False

            db.session.commit()
            flash("Defecto actualizado correctamente.", "success")
        else:
            flash("No tienes permisos para modificar este defecto.", "warning")

        return redirect(url_for('defects_bp.index'))

    return render_template('defects/edit.html', defect=defect, usuarios=usuarios)


@defects_bp.route('/<int:id>/delete', methods=['POST'])
@role_required('admin', 'miembro')
def delete(id):
    defect = Defect.query.get_or_404(id)
    db.session.delete(defect)
    db.session.commit()
    flash("Defecto eliminado correctamente.", "success")
    return redirect(url_for('defects.index'))
