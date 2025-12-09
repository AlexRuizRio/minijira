from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app import db
import os
from werkzeug.utils import secure_filename
from app.models.testcase_model import TestCase, EstadoEnum, PrioridadEnum, TipoTestEnum
from app.models.testcycle_model import TestCycle
from app.models.result_model import Result
from app.models.testcycle_model import EstadoEnum as EstadoCycleEnum
from sqlalchemy.orm import joinedload

test_bp = Blueprint('test_bp', __name__)

@test_bp.route('/tests')
def index():
    test_cases = TestCase.query.all()
    test_cycles = TestCycle.query.all()

    last_results = {}
    for tc in test_cases:
        if hasattr(tc, "resultados") and tc.resultados:
            last_results[tc.id] = sorted(tc.resultados, key=lambda r: r.fecha_created, reverse=True)[0]
        else:
            last_results[tc.id] = None

    return render_template(
        'tests/index.html',
        test_cases=test_cases,
        test_cycles=test_cycles,
        last_results=last_results
    )

@test_bp.route('/tests/<int:id>')
def show(id):
    test_case = TestCase.query.get_or_404(id)
    resultados = sorted(test_case.resultados, key=lambda r: r.fecha_created, reverse=True) if hasattr(test_case, "resultados") else []
    test_cycles = test_case.test_cycles if hasattr(test_case, "test_cycles") else []

    defectos_cerrados = []
    for r in resultados:
        if hasattr(r, 'defects'):
            for d in r.defects:
                if d.estado == 'Cerrado':
                    defectos_cerrados.append(d)

    return render_template(
        'test_cases/show.html',
        test_case=test_case,
        resultados=resultados,
        test_cycles=test_cycles,
        defectos_cerrados=defectos_cerrados
    )


# Crear TestCase
@test_bp.route('/tests/create', methods=['GET', 'POST'])
def create_test_case():
    if request.method == 'POST':
        nombre = request.form['nombre']
        objetivo = request.form.get('objetivo')
        precondicion = request.form.get('precondicion')
        descripcion = request.form.get('descripcion')
        url = request.form.get('url')
        resultado_esperado = request.form.get('resultado_esperado')
        pasos_repro = request.form.get('pasos_repro')
        estado = EstadoEnum(request.form.get('estado'))
        prioridad = PrioridadEnum(request.form.get('prioridad'))
        tipo = TipoTestEnum(request.form.get('tipo'))

        test_script = request.form.get('test_script')
        usu_created = session.get('username', 'Desconocido')

        # ---- ARCHIVO EXCEL / CSV ----
        archivo_subido = request.files.get("archivo_excel")
        archivo_excel = None

        if archivo_subido and archivo_subido.filename.strip():
            filename = secure_filename(archivo_subido.filename)
            archivo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            archivo_subido.save(archivo_path)
            archivo_excel = filename

        nuevo_test = TestCase(
            nombre=nombre,
            objetivo=objetivo,
            precondicion=precondicion,
            descripcion=descripcion,
            url = url,
            resultado_esperado = resultado_esperado,
            pasos_repro = pasos_repro,
            estado=estado,
            prioridad=prioridad,
            tipo=tipo,
            test_script=test_script,
            usu_created=usu_created,
            archivo_excel=archivo_excel
        )

        db.session.add(nuevo_test)
        db.session.commit()

        flash("Test Case creado correctamente.", "success")
        return redirect(url_for('test_bp.index'))

    return render_template(
        'test_cases/form.html',
        test_case=None,
        EstadoEnum=EstadoEnum,
        PrioridadEnum=PrioridadEnum,
        TipoTestEnum=TipoTestEnum
    )


# Editar TestCase
@test_bp.route('/tests/edit/<int:id>', methods=['GET', 'POST'])
def edit_test_case(id):
    test_case = TestCase.query.get_or_404(id)

    if request.method == 'POST':
        test_case.nombre = request.form['nombre']
        test_case.objetivo = request.form.get('objetivo')
        test_case.precondicion = request.form.get('precondicion')
        test_case.descripcion = request.form.get('descripcion')

        test_case.estado = EstadoEnum(request.form.get('estado'))
        test_case.prioridad = PrioridadEnum(request.form.get('prioridad'))
        test_case.tipo = TipoTestEnum(request.form.get('tipo'))

        test_case.test_script = request.form.get('test_script')

        # ---- GESTIÓN DE ARCHIVO ----
        archivo_subido = request.files.get("archivo_excel")

        if archivo_subido and archivo_subido.filename.strip():
            filename = secure_filename(archivo_subido.filename)
            archivo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            archivo_subido.save(archivo_path)
            test_case.archivo_excel = filename

        db.session.commit()

        flash("Test Case actualizado correctamente.", "success")
        return redirect(url_for('test_bp.index'))

    return render_template(
        'test_cases/form.html',
        test_case=test_case,
        EstadoEnum=EstadoEnum,
        PrioridadEnum=PrioridadEnum,
        TipoTestEnum=TipoTestEnum
    )



# Eliminar TestCase
@test_bp.route('/tests/delete/<int:id>', methods=['POST'])
def delete_test_case(id):
    test_case = TestCase.query.get_or_404(id)

    # Borrar resultados asociados
    for result in test_case.resultados:
        # Borrar defectos asociados a cada resultado
        for defect in result.defects:
            db.session.delete(defect)
        db.session.delete(result)

    # Finalmente borrar el test case
    db.session.delete(test_case)
    db.session.commit()

    flash("Test Case eliminado correctamente.", "success")
    return redirect(url_for('test_bp.index'))


# Crear nuevo ciclo
@test_bp.route('/testcycle/create', methods=['GET', 'POST'])
def create_cycle():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        estado = request.form.get('estado', 'NUEVO')  # nombre del Enum
        nuevo = TestCycle(
            nombre=nombre,
            descripcion=descripcion,
            estado=EstadoCycleEnum[estado]  # crea la instancia del Enum
        )

        db.session.add(nuevo)
        db.session.commit()
        flash('Test Cycle creado correctamente.', 'success')
        return redirect(url_for('test_bp.index'))

    # pasar Enum al template
    return render_template('test_cycles/create.html', estados=EstadoEnum)


@test_bp.route('/testcycle/<int:id>/edit', methods=['GET', 'POST'])
def edit_cycle(id):
    cycle = TestCycle.query.get_or_404(id)
    if request.method == 'POST':
        cycle.nombre = request.form['nombre']
        cycle.descripcion = request.form['descripcion']
        estado=EstadoCycleEnum[estado]
        db.session.commit()
        flash('Test Cycle actualizado correctamente.', 'success')
        return redirect(url_for('test_bp.index'))
    return render_template('test_cycles/edit.html', cycle=cycle)


@test_bp.route('/testcycle/<int:id>/delete', methods=['POST'])
def delete_cycle(id):
    cycle = TestCycle.query.get_or_404(id)
    db.session.delete(cycle)
    db.session.commit()
    flash('Test Cycle eliminado correctamente.', 'success')
    return redirect(url_for('test_bp.index'))


# Mostrar un ciclo y sus testcases
@test_bp.route('/testcycle/<int:id>')
def show_cycle(id):
    cycle = TestCycle.query.get_or_404(id)
    
    last_results = {}
    for r in cycle.resultados:
        if r.test_case_id not in last_results:
            last_results[r.test_case_id] = r
        else:
            if r.fecha_created > last_results[r.test_case_id].fecha_created:
                last_results[r.test_case_id] = r

    all_cases = TestCase.query.all()

    return render_template(
        'test_cycles/show.html',
        cycle=cycle,
        last_results=last_results,
        all_cases=all_cases
    )


# Agregar un TestCase al ciclo
@test_bp.route('/testcycle/<int:id>/add_testcase', methods=['POST'])
def add_testcase_to_cycle(id):
    cycle = TestCycle.query.get_or_404(id)
    testcase_id = request.form.get('testcase_id')
    testcase = TestCase.query.get(testcase_id)

    if testcase not in cycle.testcases:
        cycle.testcases.append(testcase)
        db.session.commit()
        flash("TestCase agregado correctamente al ciclo.", "success")
    else:
        flash("Este TestCase ya está en el ciclo.", "warning")

    return redirect(url_for('test_bp.show_cycle', id=id))


# Eliminar un TestCase del ciclo
@test_bp.route('/testcycle/<int:id>/remove_testcase/<int:testcase_id>', methods=['POST'])
def remove_testcase_from_cycle(id, testcase_id):
    cycle = TestCycle.query.get_or_404(id)
    testcase = TestCase.query.get_or_404(testcase_id)
    if testcase in cycle.testcases:
        cycle.testcases.remove(testcase)
        db.session.commit()
        flash("TestCase eliminado del ciclo.", "success")
    return redirect(url_for('test_bp.show_cycle', id=id))