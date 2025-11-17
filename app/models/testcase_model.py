from app import db
from app.models.testcase_testcycle_model import testcase_testcycle
import enum
from datetime import datetime

class TipoTestEnum(enum.Enum):
    MANUAL = "manual"
    AUTOMATIZADO = "automatizado"

class PrioridadEnum(enum.Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"

class EstadoEnum(enum.Enum):
    NUEVO = "NUEVO"
    EN_PROGRESO = "EN_PROGRESO"
    TERMINADO = "TERMINADO"
    
class TestCase(db.Model):
    __tablename__ = 'test_case'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    objetivo = db.Column(db.Text)
    precondicion = db.Column(db.Text)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.Enum(EstadoEnum))
    prioridad = db.Column(db.Enum(PrioridadEnum))
    test_script = db.Column(db.Text)
    tipo = db.Column(db.Enum(TipoTestEnum))
    fecha_created = db.Column(db.DateTime, default=datetime.utcnow)
    usu_created = db.Column(db.String(100))

    test_cycles = db.relationship(
        'TestCycle',
        secondary=testcase_testcycle,
        back_populates='testcases'
    )