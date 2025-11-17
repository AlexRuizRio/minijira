import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
import pytest

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
        yield app

@pytest.fixture
def client(app):
    """Cliente de prueba que permite hacer peticiones HTTP simuladas."""
    return app.test_client()
