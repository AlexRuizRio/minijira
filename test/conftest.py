import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
import pytest

os.environ["APP_ENV"] = "test"

@pytest.fixture
def app():
    app = create_app()

    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://root:@localhost/minijira_test",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "testing123", 
    })

    with app.app_context():

        db.create_all()
        yield app

        db.session.remove()

@pytest.fixture
def client(app):
    return app.test_client()
