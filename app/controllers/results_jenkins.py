# app/controllers/results_from_jenkins.py
from flask import Blueprint, request, jsonify
from app.models.result_model import Result, EstadoPruebaEnum
from app import db

results_bp = Blueprint('results_bp', __name__, url_prefix='/api/results')

@results_bp.post('/<int:test_case_id>/from_jenkins')
def receive_results(test_case_id):
    data = request.json

    nuevo_result = Result(
        test_case_id=test_case_id,
        estado_prueba=EstadoPruebaEnum(data.get('estado', 'EN_PROGRESO')),
        resultado_obtenido=data.get('logs', ''),
        notas=data.get('notas', ''),
        archivo=data.get('archivo'),
        usu_created='jenkins'
    )

    db.session.add(nuevo_result)
    db.session.commit()

    return jsonify({"message": "Resultado recibido"}), 200
