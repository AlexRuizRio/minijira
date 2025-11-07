from app import db
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
    NUEVO = "nuevo"
    EN_PROGRESO = "en_progreso"
    TERMINADO = "terminado"

class TestCase(db.Model):
    __tablename__ = 'test_case'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    objetivo = db.Column(db.Text)
    precondicion = db.Column(db.Text)
    estado = db.Column(db.Enum(EstadoEnum))
    prioridad = db.Column(db.Enum(PrioridadEnum))
    test_script = db.Column(db.Text)
    tipo = db.Column(db.Enum(TipoTestEnum))
    fecha_created = db.Column(db.DateTime, default=datetime.utcnow)
    usu_created = db.Column(db.String(100))
