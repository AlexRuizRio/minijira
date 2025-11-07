from app import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(
        db.Enum('Activo', 'En pausa', 'Cerrado', name='estado_proyecto'),
        default='Activo'
    )
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, nullable=True)

    # 🔹 Usuario que creó el proyecto
    user_created = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creador = db.relationship('User', back_populates='proyectos_creados')

    # Relación con EpicHU
    epics = db.relationship('EpicHU', back_populates='proyecto', lazy=True)

    def __repr__(self):
        return f"<Proyecto {self.nombre}>"
