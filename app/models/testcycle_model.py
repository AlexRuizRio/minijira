from app import db
from app.models.testcase_testcycle_model import testcase_testcycle
from app.models.result_model import Result
import enum

class EstadoEnum(enum.Enum):
    NUEVO = "nuevo"
    EN_PROGRESO = "en_progreso"
    TERMINADO = "terminado"

class TestCycle(db.Model):
    __tablename__ = 'test_cycle'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    estado = db.Column(db.Enum(EstadoEnum))

    testcases = db.relationship(
        'TestCase',
        secondary=testcase_testcycle,
        back_populates='test_cycles'
    )

    resultados = db.relationship(
        'Result',
        back_populates='test_cycle',
        cascade='all, delete-orphan',
        lazy=True
    )