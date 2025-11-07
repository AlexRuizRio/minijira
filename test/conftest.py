import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
import pytest
from app.models.user_model import User, Role

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://root:@localhost/minijira_test",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "testsecret"
    })

    with app.app_context():
        # Limpiar la base de datos antes de cada test
        db.drop_all()
        db.create_all()

        # Insertar datos base
        admin_role = Role(nombre="admin", descripcion="Administrador")
        user_role = Role(nombre="viewer", descripcion="Solo lectura")

        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("1234")
        admin_user.roles.append(admin_role)

        viewer_user = User(username="viewer", email="viewer@test.com")
        viewer_user.set_password("1234")
        viewer_user.roles.append(user_role)

        db.session.add_all([admin_role, user_role, admin_user, viewer_user])
        db.session.commit()

        yield app

        # Limpiar después de los tests
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de prueba que permite hacer peticiones HTTP simuladas."""
    return app.test_client()
