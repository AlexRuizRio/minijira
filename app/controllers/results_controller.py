# app/controllers/results_controller.py
from flask import Blueprint, request, redirect, url_for, flash, render_template
from app import db
from app.models.result_model import Result, EstadoPruebaEnum
from app.models.testcase_model import TestCase
from app.models.defect_model import Defect
from app.models.user_model import User
from datetime import datetime
from app.utils.decorators import role_required

results_bp = Blueprint('results', __name__, url_prefix='/results')
URL_RESULT = 'test_bp.show'


@results_bp.route('/<int:id>')
def show(id):
    result = Result.query.get_or_404(id)
    return render_template('results/edit.html', result=result)


# ---------- CREATE ----------
@results_bp.route('/create/<int:test_case_id>', methods=['POST'])
def create(test_case_id):
    test_case = TestCase.query.get_or_404(test_case_id)

    estado_prueba = request.form['estado_prueba']
    entorno = request.form.get('entorno')
    url = request.form.get('url')
    usu_created = request.form.get('usu_created')
    resultado_esperado = request.form.get('resultado_esperado')
    resultado_obtenido = request.form.get('resultado_obtenido')
    pasos_repro = request.form.get('pasos_repro')
    notas = request.form.get('notas')

    test_cycle_id = request.form.get('test_cycle_id')
    crear_defecto_auto = 'crear_defecto_auto' in request.form  # checkbox

    nuevo_resultado = Result(
        test_case_id=test_case.id,
        test_cycle_id=test_cycle_id if test_cycle_id else None,
        estado_prueba=EstadoPruebaEnum(estado_prueba),
        entorno=entorno,
        url=url,
        usu_created=usu_created,
        resultado_esperado=resultado_esperado,
        resultado_obtenido=resultado_obtenido,
        pasos_repro=pasos_repro,
        notas=notas,
    )

    db.session.add(nuevo_resultado)
    db.session.commit()

    # Crear defecto SOLO si el estado es "fallido" y el checkbox está marcado
    if estado_prueba == "fallido" and crear_defecto_auto:
        defecto = Defect(
            test_case_id=test_case.id,
            result_id=nuevo_resultado.id,
            titulo=f"Defecto generado por resultado #{nuevo_resultado.id}",
            descripcion=resultado_obtenido or "Sin descripción",
            estado="Abierto",
            prioridad="Media",
            verificado=False
        )
        db.session.add(defecto)
        db.session.commit()

    # Si el resultado es PASADO, marcar como verificados los defectos cerrados pendientes
    elif estado_prueba == "pasado":
        defectos_pendientes = Defect.query.filter_by(
            test_case_id=test_case.id,
            estado="Cerrado",
            verificado=False
        ).all()
        for defect in defectos_pendientes:
            defect.verificado = True
        db.session.commit()

    flash("Resultado creado correctamente.", "success")
    return redirect(url_for(URL_RESULT, id=test_case.id))



# ---------- EDIT ----------
@results_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin', 'miembro', redirect_to='project_bp.index')
def edit(id):
    result = Result.query.get_or_404(id)

    if request.method == 'POST':
        # ELIMINAR
        if 'delete' in request.form:
            # Eliminar defectos asociados
            Defect.query.filter_by(result_id=result.id).delete()
            db.session.delete(result)
            db.session.commit()
            flash('Resultado y defectos asociados eliminados correctamente.', 'success')
            return redirect(url_for(URL_RESULT, id=result.test_case_id))

        # EDITAR
        result.estado_prueba = EstadoPruebaEnum(request.form['estado_prueba'])
        result.entorno = request.form.get('entorno')
        result.url = request.form.get('url')
        result.resultado_esperado = request.form.get('resultado_esperado')
        result.resultado_obtenido = request.form.get('resultado_obtenido')
        result.notas = request.form.get('notas')

        db.session.commit()

        # Crear defecto si cambia a fallido y no hay defecto existente
        if result.estado_prueba.value == "fallido" and not result.defect:
            defecto = Defect(
                test_case_id=result.test_case_id,
                result_id=result.id,
                titulo=f"Defecto generado por resultado #{result.id}",
                descripcion=result.resultado_obtenido or "Sin descripción",
                estado="Abierto",
                prioridad="Media"
            )
            db.session.add(defecto)
            db.session.commit()

        flash('Resultado actualizado correctamente.', 'success')
        return redirect(url_for(URL_RESULT, id=result.test_case_id))

    return render_template('results/edit.html', result=result)


# ---------- DELETE ----------
@results_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    result = Result.query.get_or_404(id)

    # Eliminar defectos asociados
    Defect.query.filter_by(result_id=result.id).delete()
    
    test_case_id = result.test_case_id
    db.session.delete(result)
    db.session.commit()

    flash('Resultado y defectos asociados eliminados correctamente.', 'success')
    return redirect(url_for(URL_RESULT, id=test_case_id))