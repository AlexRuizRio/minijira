from app import db
import enum
from datetime import datetime

class EstadoPruebaEnum(enum.Enum):
    PASADO = "pasado"
    FALLIDO = "fallido"
    BLOQUEADO = "bloqueado"
    EN_PROGRESO = "en_progreso"

class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True)

    # Relaciones
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=False)
    test_cycle_id = db.Column(db.Integer, db.ForeignKey('test_cycle.id'))
    test_case = db.relationship('TestCase', backref='resultados', lazy=True)
    test_cycle = db.relationship('TestCycle', back_populates='resultados', lazy=True)


    # Información de la ejecución
    estado_prueba = db.Column(db.Enum(EstadoPruebaEnum), nullable=False)
    entorno = db.Column(db.String(100))
    resultado_obtenido = db.Column(db.Text)               
    notas = db.Column(db.Text)
    archivo = db.Column(db.String(255), nullable=True)
    # Auditoría
    fecha_created = db.Column(db.DateTime, default=datetime.utcnow)
    usu_created = db.Column(db.String(100))

    def __repr__(self):
        return f"<Result TestCase={self.test_case_id} Estado={self.estado_prueba.value}>"
