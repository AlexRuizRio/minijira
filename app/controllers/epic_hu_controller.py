from flask import Blueprint, render_template
from app.models.epic_hu_model import EpicHU  

epic_bp = Blueprint('epic_bp', __name__)

@epic_bp.route('/epics')
def index():
    # Cargamoslas épicas 
    epics = EpicHU.query.filter_by(tipo='epic').all()
    return render_template('epics/index.html', epics=epics)

@epic_bp.route('/epic/<int:id>')
def detalle_epic(id):
    epic = EpicHU.query.get_or_404(id)
    # Historias hijas relacionadas con esta épica
    hus = EpicHU.query.filter_by(epica_id=id).all()
    return render_template('epics/detalle.html', epic=epic, hus=hus)

@epic_bp.route('/hu/<int:id>')
def detalle_hu(id):
    hu = EpicHU.query.get_or_404(id)
    return render_template('epics/hu_detalle.html', hu=hu)
