from flask import Flask, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)

    # Configuración base
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'supersecreto'

    # Si se pasa configuración de test (por pytest o manualmente)
    if test_config:
        app.config.update(test_config)

    # Si no hay configuración de test, detectar entorno
    else:
        # Leer variable de entorno APP_ENV (puede ser: dev, test, prod)
        env = os.getenv("APP_ENV", "dev")
        print("APP_ENV detectado:", os.getenv("APP_ENV"))
        if env == "test":
            app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/minijira_test'
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/minijira'

    # Inicializar DB
    db.init_app(app)

    # Importar y registrar blueprints
    from app.controllers.project_controller import project_bp
    from app.controllers.epic_hu_controller import epic_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.user_controller import user_bp
    from app.controllers.test_controller import test_bp
    from app.controllers.results_controller import results_bp
    from app.controllers.defects_controller import defects_bp

    app.register_blueprint(defects_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(epic_bp)

    # Ruta raíz
    @app.route('/')
    def home_redirect():
        if 'user_id' in session:
            return redirect(url_for('project_bp.index'))
        else:
            return redirect(url_for('auth_bp.login'))

    return app
