from app import db
import enum
from datetime import datetime

class TipoEnum(enum.Enum):
    EPIC = "epic"
    HU = "hu"

class PrioridadEnum(enum.Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"

class EstadoEnum(enum.Enum):
    NUEVO = "nuevo"
    EN_PROGRESO = "en_progreso"
    TERMINADO = "terminado"

class EpicHU(db.Model):
    __tablename__ = 'epic_hu'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.Enum(TipoEnum))
    prioridad = db.Column(db.Enum(PrioridadEnum))
    nombre = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    epica_id = db.Column(db.Integer, db.ForeignKey('epic_hu.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    estado = db.Column(db.Enum(EstadoEnum))
    fecha_created = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    usu_created = db.Column(db.String(100))

    # Relación consigo mismo (HUs hijas)
    hus = db.relationship('EpicHU', backref=db.backref('epica', remote_side=[id]))

    # Relaciones N:M
    test_cases = db.relationship('TestCase', secondary='epic_testcase', backref='epics')
    test_cycles = db.relationship('TestCycle', secondary='epic_testcycle', backref='epics')

    # Relación con Project
    proyecto = db.relationship('Project', back_populates='epics')

