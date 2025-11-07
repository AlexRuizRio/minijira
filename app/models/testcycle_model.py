from app import db
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
