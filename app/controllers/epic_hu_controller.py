from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.testcase_model import TestCase
from app.models.testcycle_model import TestCycle
from app.models.epic_hu_model import EpicHU, TipoEnum, EstadoEnum, PrioridadEnum
from app import db

epic_bp = Blueprint('epic_bp', __name__)

# --- LISTADO DE ÉPICAS ---
@epic_bp.route('/epics')
def index():
    epics = EpicHU.query.filter_by(tipo='epic').all()
    return render_template('epics/index.html', epics=epics)

# --- DETALLE DE ÉPICA ---
@epic_bp.route('/epic/<int:id>')
def detalle_epic(id):
    epic = EpicHU.query.get_or_404(id)

    # Historias asociadas a esta épica
    hus = EpicHU.query.filter_by(epica_id=id).all()

    # Historias disponibles (de tipo HU, sin épica asignada)
    all_hus = EpicHU.query.filter(
        EpicHU.tipo == TipoEnum.HU,
        EpicHU.epica_id.is_(None)
    ).all()

    return render_template('epics/detalle.html', epic=epic, hus=hus, all_hus=all_hus)


# --- ASOCIAR HU A ÉPICA ---
@epic_bp.route('/epic/<int:epic_id>/asociar_hu', methods=['POST'])
def asociar_hu(epic_id):
    epic = EpicHU.query.get_or_404(epic_id)
    hu_id = request.form.get('hu_id')
    if hu_id:
        hu = EpicHU.query.get(hu_id)
        if hu and hu.epica_id is None:
            hu.epica_id = epic.id
            db.session.commit()
            flash(f"Historia de Usuario '{hu.nombre}' asociada correctamente a la épica '{epic.nombre}'.", "success")
    return redirect(url_for('epic_bp.detalle_epic', id=epic_id))


# --- DETALLE DE HU ---
@epic_bp.route('/hu/<int:id>')
def detalle_hu(id):
    hu = EpicHU.query.get_or_404(id)
    all_test_cases = TestCase.query.filter(~TestCase.epics.any(id=hu.id)).all()
    all_test_cycles = TestCycle.query.filter(~TestCycle.epics.any(id=hu.id)).all()
    return render_template('epics/hu_detalle.html', hu=hu, all_test_cases=all_test_cases, all_test_cycles=all_test_cycles)


# --- ASOCIAR TEST CASE A HU ---
@epic_bp.route('/hu/<int:hu_id>/asociar_test_case', methods=['POST'])
def asociar_test_case(hu_id):
    hu = EpicHU.query.get_or_404(hu_id)
    test_case_id = request.form.get('test_case_id')

    if test_case_id:
        tc = TestCase.query.get(test_case_id)
        if tc and tc not in hu.test_cases:
            hu.test_cases.append(tc)
            db.session.commit()
            flash(f"Test Case '{tc.nombre}' asociado correctamente.", "success")

    return redirect(url_for('epic_bp.detalle_hu', id=hu_id))

# --- DETALLE DE TEST CASE ---
@epic_bp.route('/tests/<int:id>')
def detalle_test_case(id):
    test_case = TestCase.query.get_or_404(id)
    return render_template('tests/detalle.html', test_case=test_case)


# --- ASOCIAR TEST CYCLE A HU ---
@epic_bp.route('/hu/<int:hu_id>/asociar_test_cycle', methods=['POST'])
def asociar_test_cycle(hu_id):
    from app.models.testcycle_model import TestCycle  # importa aquí para evitar loops
    hu = EpicHU.query.get_or_404(hu_id)
    test_cycle_id = request.form.get('test_cycle_id')

    if test_cycle_id:
        tc = TestCycle.query.get(test_cycle_id)
        if tc and tc not in hu.test_cycles:
            hu.test_cycles.append(tc)
            db.session.commit()
            flash(f"Test Cycle '{tc.nombre}' asociado correctamente.", "success")

    return redirect(url_for('epic_bp.detalle_hu', id=hu_id))

# --- DESASOCIAR TEST CASE DE HU ---
@epic_bp.route('/hu/<int:hu_id>/remove_test_case/<int:tc_id>', methods=['POST'])
def remove_test_case(hu_id, tc_id):
    hu = EpicHU.query.get_or_404(hu_id)
    tc = TestCase.query.get_or_404(tc_id)
    if tc in hu.test_cases:
        hu.test_cases.remove(tc)
        db.session.commit()
        flash(f"Relación con el Test Case '{tc.nombre}' eliminada.", "info")
    return redirect(url_for('epic_bp.detalle_hu', id=hu_id))

# --- DESASOCIAR TEST CYCLE DE HU ---
@epic_bp.route('/hu/<int:hu_id>/remove_test_cycle/<int:cycle_id>', methods=['POST'])
def remove_test_cycle(hu_id, cycle_id):
    from app.models.testcycle_model import TestCycle
    hu = EpicHU.query.get_or_404(hu_id)
    cycle = TestCycle.query.get_or_404(cycle_id)
    if cycle in hu.test_cycles:
        hu.test_cycles.remove(cycle)
        db.session.commit()
        flash(f"Relación con el Test Cycle '{cycle.nombre}' eliminada.", "info")
    return redirect(url_for('epic_bp.detalle_hu', id=hu_id))

@epic_bp.route('/crear_epic_hu', methods=['POST'])
def crear_epic_hu():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    tipo = request.form.get('tipo')
    prioridad = request.form.get('prioridad') or 'MEDIA'
    estado = request.form.get('estado') or 'NUEVO'
    epica_id = request.form.get('epica_id') or None

    nueva = EpicHU(
        nombre=nombre,
        descripcion=descripcion,
        tipo=TipoEnum[tipo],
        prioridad=PrioridadEnum[prioridad],
        estado=EstadoEnum[estado],
        epica_id=epica_id
    )

    db.session.add(nueva)
    db.session.commit()
    flash(f"{tipo} '{nombre}' creada correctamente.", "success")
    return redirect(url_for('epic_bp.index'))
