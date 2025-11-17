# app/models/defect_model.py
from app import db
from datetime import datetime

class Defect(db.Model):
    __tablename__ = 'defect'

    id = db.Column(db.Integer, primary_key=True)
    
    # Relación con TestCase y Result (ahora opcionales)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=True)
    
    # Información del defecto
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(50), default="Abierto")  # Abierto, En progreso, Cerrado
    prioridad = db.Column(db.String(50), default="Media") # Baja, Media, Alta
    verificado = db.Column(db.Boolean, default=False)

    # Usuario asignado
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to = db.relationship('User', backref='defects', lazy=True)

    # Auditoría
    fecha_created = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relaciones (ahora opcionales)
    test_case = db.relationship('TestCase', backref='defects', lazy=True)
    result = db.relationship('Result', backref='defects', lazy=True)

    def __repr__(self):
        return f"<Defect #{self.id} Estado={self.estado} TestCase={self.test_case_id}>"
