from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

user_role = db.Table('user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_created = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship('Role', secondary=user_role, back_populates='usuarios')
    proyectos_creados = db.relationship('Project', back_populates='creador', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True)
    descripcion = db.Column(db.Text)

    usuarios = db.relationship('User', secondary=user_role, back_populates='roles')
