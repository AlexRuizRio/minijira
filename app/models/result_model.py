from app import db
import enum
from datetime import datetime

class EstadoPruebaEnum(enum.Enum):
    PASADO = "pasado"
    FALLIDO = "fallido"
    BLOQUEADO = "bloqueado"

class Result(db.Model):
    __tablename__ = 'resultado'

    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'))
    test_cycle_id = db.Column(db.Integer, db.ForeignKey('test_cycle.id'))
    estado_prueba = db.Column(db.Enum(EstadoPruebaEnum))
    fecha_created = db.Column(db.DateTime, default=datetime.utcnow)
    usu_created = db.Column(db.String(100))

    test_case = db.relationship('TestCase', backref='resultados')
    test_cycle = db.relationship('TestCycle', backref='resultados')
