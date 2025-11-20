import subprocess
import tempfile
from flask import Blueprint, redirect, url_for, flash
from app import db
from app.models.testcase_model import TestCase

automatizacion_bp = Blueprint("automatizacion", __name__, url_prefix="/automatizacion")

@automatizacion_bp.post("/run/<int:id>")
def run_test(id):
    testcase = TestCase.query.get_or_404(id)

    # Guardamos el script temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(testcase.test_script.encode())
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout
        error = result.stderr

        if "OK" in output:
            testcase.estado = "TERMINADO"
            flash("Test Ejecutado: PASADO ✔", "success")
        else:
            testcase.estado = "EN_PROGRESO"
            flash("Test Ejecutado: FALLIDO ❌", "danger")

        testcase.descripcion = f"Output:\n{output}\n\nError:\n{error}"

    except Exception as e:
        testcase.estado = "EN_PROGRESO"
        testcase.descripcion = f"EXCEPCIÓN FATAL:\n{str(e)}"
        flash("El test falló con una excepción", "danger")

    finally:
        db.session.commit()

    return redirect(url_for('test_bp.show', id=testcase.id))
