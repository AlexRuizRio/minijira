# app/controllers/run_test_controller.py
import requests
from flask import Blueprint, jsonify, current_app
from app.models.testcase_model import TestCase

run_bp = Blueprint('run_bp', __name__, url_prefix='/run')

@run_bp.post('/test/<int:test_case_id>')
def run_test(test_case_id):
    test_case = TestCase.query.get_or_404(test_case_id)

    # Solo para tests AUTOMATIZADOS
    if test_case.tipo.value != "automatizado":
        return jsonify({"error": "Este test no es automatizado"}), 400

    payload = {
        "test_script": test_case.test_script,
        "entorno": "staging",  # o coger del usuario
        "test_case_id": test_case.id,
        "archivo_excel": test_case.archivo_excel
    }

    # URL del job de Jenkins
    jenkins_url = current_app.config['JENKINS_URL'] + "/job/ejecutar_test/buildWithParameters"
    jenkins_user = current_app.config['JENKINS_USER']
    jenkins_token = current_app.config['JENKINS_TOKEN']

    response = requests.post(jenkins_url, params=payload, auth=(jenkins_user, jenkins_token))

    if response.status_code == 201:
        return jsonify({"message": "Test enviado a Jenkins"}), 200
    else:
        return jsonify({"error": "Error enviando test a Jenkins", "details": response.text}), 500
