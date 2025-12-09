# app/controllers/results_controller.py
from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app, send_from_directory
import os
from app import db
from app.models.result_model import Result, EstadoPruebaEnum
from app.models.testcase_model import TestCase
from app.models.defect_model import Defect
from datetime import datetime
from app.utils.decorators import role_required
from werkzeug.utils import secure_filename

results_bp = Blueprint('results', __name__, url_prefix='/results')
URL_RESULT = 'test_bp.show'

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/uploads/<path:filename>')
def serve(filename):
    """Devuelve el archivo desde UPLOAD_FOLDER"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

def _ensure_upload_folder():
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        # por defecto crea carpeta 'uploads' en el root del proyecto
        upload_folder = os.path.join(os.getcwd(), 'uploads')
        current_app.config['UPLOAD_FOLDER'] = upload_folder
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

# ---------- SHOW ----------
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
    resultado_obtenido = request.form.get('resultado_obtenido')
    notas = request.form.get('notas')
    usu_created = request.form.get('usu_created')

    test_cycle_id = request.form.get('test_cycle_id')

    # checkbox para crear defecto automático (debe existir en el form con name="crear_defecto_auto")
    crear_defecto_auto = 'crear_defecto_auto' in request.form

    # manejo de fichero
    archivo_filename = None
    archivo_subido = request.files.get("archivo")
    if archivo_subido and archivo_subido.filename and archivo_subido.filename.strip():
        upload_folder = _ensure_upload_folder()
        filename = secure_filename(archivo_subido.filename)
        archivo_path = os.path.join(upload_folder, filename)
        archivo_subido.save(archivo_path)
        archivo_filename = filename

    # Crear resultado
    nuevo_resultado = Result(
        test_case_id=test_case.id,
        test_cycle_id=int(test_cycle_id) if test_cycle_id else None,
        estado_prueba=EstadoPruebaEnum(estado_prueba),
        entorno=entorno,
        resultado_obtenido=resultado_obtenido,
        notas=notas,
        usu_created=usu_created,
        archivo=archivo_filename  # requiere que Result tenga la columna 'archivo'
    )

    db.session.add(nuevo_resultado)
    db.session.commit()

    # Crear defecto automáticamente si FALLA y el checkbox está marcado
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

    # Si PASA → marcar defectos cerrados como verificados
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
            # eliminar defectos asociados (si quieres)
            Defect.query.filter_by(result_id=result.id).delete()
            test_case_id = result.test_case_id

            db.session.delete(result)
            db.session.commit()

            flash('Resultado y defectos asociados eliminados correctamente.', 'success')
            return redirect(url_for(URL_RESULT, id=test_case_id))

        # ------ ACTUALIZAR CAMPOS ------
        # Nota: request.form['estado_prueba'] debe ser 'pasado'|'fallido'|'bloqueado'|'en_progreso'
        result.estado_prueba = EstadoPruebaEnum(request.form['estado_prueba'])
        result.entorno = request.form.get('entorno')
        result.resultado_obtenido = request.form.get('resultado_obtenido')
        result.notas = request.form.get('notas')

        # ------ ARCHIVO (posible reemplazo) ------
        archivo_subido = request.files.get("archivo")
        if archivo_subido and archivo_subido.filename and archivo_subido.filename.strip():
            upload_folder = _ensure_upload_folder()
            filename = secure_filename(archivo_subido.filename)
            archivo_path = os.path.join(upload_folder, filename)
            archivo_subido.save(archivo_path)
            result.archivo = filename

        db.session.commit()

        # Crear defecto si cambia a fallido y no hay uno existente
        if result.estado_prueba.value == "fallido":
            # si quieres comprobar existencia de defect existente relacionado con este result:
            existe_defect = Defect.query.filter_by(result_id=result.id).first()
            if not existe_defect:
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
