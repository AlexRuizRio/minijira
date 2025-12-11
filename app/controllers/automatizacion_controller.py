import subprocess, requests
import tempfile
import os, re
import json
from flask import Blueprint, redirect, url_for, flash, jsonify, request
from app import db
from app.models.testcase_model import TestCase, EstadoEnum
from app.models.result_model import Result, EstadoPruebaEnum


automatizacion_bp = Blueprint("automatizacion", __name__, url_prefix="/automatizacion")


@automatizacion_bp.post("/run/local/<int:test_case_id>")
def run_test(test_case_id):
    testcase = TestCase.query.get_or_404(id)

    # Detectar tipo de ejecución
    script_raw = testcase.test_script.strip()
    primera_linea = script_raw.splitlines()[0].lower()

    if primera_linea.startswith("#gherkin"):
        modo = "gherkin"
    else:
        modo = "selenium"

    print(">>> Modo ejecución:", modo)

    output = ""
    error = ""
    data = None  # variable para el JSON de behave (si aplica)

    try:
        # ===========================================
        #   MODO SELENIUM
        # ===========================================
        if modo == "selenium":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(script_raw.encode())
                temp_path = f.name

            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout or ""
            error = result.stderr or ""

        # ===========================================
        #   MODO GHERKIN
        # ===========================================
        else:
            temp_dir = tempfile.mkdtemp()
            features_dir = os.path.join(temp_dir, "features")
            steps_dir = os.path.join(features_dir, "steps")
            os.makedirs(steps_dir)

            # Copiar steps reales
            with open("features/steps/steps.py", "r", encoding="utf8") as src, \
                 open(os.path.join(steps_dir, "steps.py"), "w", encoding="utf8") as dst:
                dst.write(src.read())

            # Copiar environment si existe
            if os.path.exists("features/environment.py"):
                with open("features/environment.py", "r", encoding="utf8") as src, \
                     open(os.path.join(features_dir, "environment.py"), "w", encoding="utf8") as dst:
                    dst.write(src.read())

            # Guardar feature
            with open(os.path.join(features_dir, "test.feature"), "w", encoding="utf8") as f:
                f.write(script_raw.replace("#gherkin", "").strip())

            # Ejecutar behave con salida JSON a fichero temporal
            json_result_path = os.path.join(temp_dir, "resultado.json")
            result = subprocess.run(
                ["behave", features_dir, "--no-capture"],
                capture_output=True,
                text=True,
                timeout=60
            )


            output = result.stdout or ""
            error = result.stderr or ""

       # ============================================================
        # VALIDACIÓN POR PALABRA CLAVE DEL THEN FINAL
        # ============================================================

        logs = f"{output}\n{error}"

        # Esperado (texto exacto que el usuario configuró)
        esperado = (testcase.resultado_esperado or "").strip()

        # Si no hay esperado, marcamos fallo
        if not esperado:
            encontrado = None
        else:
            # Buscar literalmente la palabra esperada en todo el log
            patron = rf"\b{re.escape(esperado)}\b"
            match = re.search(patron, logs)

            if match:
                encontrado = match.group(0)  # Ej: "OK"
            else:
                encontrado = None

        # Decisión final basada solo en si encontramos ese texto
        if encontrado:
            estado_prueba = EstadoPruebaEnum.PASADO
            testcase.estado = "TERMINADO"
            flash("Test Ejecutado: PASADO ✔", "success")
        else:
            estado_prueba = EstadoPruebaEnum.FALLIDO
            testcase.estado = "EN_PROGRESO"
            flash("Test Ejecutado: FALLIDO ❌", "danger")

        # Guardar traza completa en la descripción
        testcase.descripcion = logs

        # Registrar resultado
        nuevo_resultado = Result(
            test_case_id=testcase.id,
            estado_prueba=estado_prueba,
            entorno="Automatizado",
            resultado_obtenido=encontrado or "",
            notas=logs,
            usu_created="Sistema"
        )
        db.session.add(nuevo_resultado)



    except Exception as e:
        testcase.estado = "EN_PROGRESO"
        testcase.descripcion = f"EXCEPCIÓN FATAL:\n{str(e)}"
        nuevo_resultado = Result(
            test_case_id=testcase.id,
            estado_prueba=EstadoPruebaEnum.FALLIDO,
            entorno="Automatizado",
            resultado_obtenido=str(e),
            notas="Excepción durante ejecución",
            usu_created="Sistema"
        )
        db.session.add(nuevo_resultado)
        flash("El test falló con una excepción ❌", "danger")

    finally:
        db.session.commit()

    return redirect(url_for('test_bp.show', id=testcase.id))


import requests
from flask import flash, redirect, url_for



@automatizacion_bp.post("/run/jenkins/<int:test_case_id>")
def run_test_case(test_case_id):
    test_case = TestCase.query.get_or_404(test_case_id)

    JENKINS_URL = "http://localhost:8080"     # sin slash final
    JOB = "Pipeline"
    USER = ""                      # <- usar username real
    API_TOKEN = ""                # <- generar en Jenkins (user > Configure > API Token)
    TOKEN_BUILD = ""          # token del job (Trigger builds remotely)

    session = requests.Session()
    session.auth = (USER, API_TOKEN)

    # 1) Verificar credenciales (opcional pero útil)
    try:
        me = session.get(f"{JENKINS_URL}/api/json", timeout=10)
    except Exception as e:
        flash(f"Error conectando a Jenkins: {e}", "danger")
        return redirect(url_for('test_bp.show', id=test_case_id))

    if me.status_code != 200:
        flash(f"Credenciales inválidas o Jenkins inaccesible (status {me.status_code}).", "danger")
        return redirect(url_for('test_bp.show', id=test_case_id))

    # 2) Obtener crumb (CSRF)
    crumb_field = None
    crumb_value = None
    try:
        crumb_resp = session.get(f"{JENKINS_URL}/crumbIssuer/api/json", timeout=10)
        if crumb_resp.status_code == 200:
            crumb_json = crumb_resp.json()
            crumb_field = crumb_json.get("crumbRequestField")
            crumb_value = crumb_json.get("crumb")
        else:
            # 401 -> credenciales; 404 -> crumb issuer desactivado (no debería pasar si CSRF on)
            flash(f"Error obteniendo crumb ({crumb_resp.status_code}).", "danger")
            return redirect(url_for('test_bp.show', id=test_case_id))
    except Exception as e:
        flash(f"Excepción al pedir crumb: {e}", "danger")
        return redirect(url_for('test_bp.show', id=test_case_id))

    # 3) Preparar payload y headers
    payload = {
        "TEST_SCRIPT": test_case.test_script or "",
        "TEST_CASE_ID": str(test_case.id),
        "ENTORNO": "staging",
        "USUARIO": "alex"
    }

    headers = {}
    if crumb_field and crumb_value:
        headers[crumb_field] = crumb_value

    build_url = f"{JENKINS_URL}/job/{JOB}/buildWithParameters?token={TOKEN_BUILD}"

    # 4) Lanzar build
    resp = session.post(build_url, data=payload, headers=headers, timeout=30)

    # Debug prints (útiles en logs)
    print("CRUMB:", crumb_field, crumb_value)
    print("BUILD URL:", build_url)
    print("STATUS:", resp.status_code)
    print(resp.text[:1000])

    if resp.status_code in (200, 201, 202):   # 201/202 pueden aparecer
        flash("Prueba enviada a Jenkins correctamente ✔", "success")
    else:
        flash(f"Error lanzando build en Jenkins (status {resp.status_code}). Revisa logs.", "danger")

    return redirect(url_for('test_bp.show', id=test_case_id))

@automatizacion_bp.post("/run/cycle/jenkins/<int:cycle_id>")
def run_cycle_in_jenkins(cycle_id):
    from app.models.testcase_model import TestCase
    from app.models.testcycle_model import TestCycle
    from flask import redirect, url_for, flash
    import requests

    cycle = TestCycle.query.get_or_404(cycle_id)

    if not cycle.testcases:
        flash("Este ciclo no tiene TestCases asignados.", "warning")
        return redirect(url_for('test_bp.show_cycle', id=cycle_id))

    # -----------------------------
    # CONFIG JENKINS
    # -----------------------------
    JENKINS_URL = "http://localhost:8080"
    JOB = "Pipeline"
    USER = "ardelrio"
    API_TOKEN = "11c4d543e2c72cacdfe6dcb4702548b630"
    TOKEN_BUILD = "MI_TOKEN_JENKINS"

    session = requests.Session()
    session.auth = (USER, API_TOKEN)

    # Verificar conexión
    try:
        me = session.get(f"{JENKINS_URL}/api/json", timeout=10)
        if me.status_code != 200:
            flash("No se pudo conectar a Jenkins (credenciales/servidor).", "danger")
            return redirect(url_for('test_bp.show_cycle', id=cycle_id))
    except Exception as e:
        flash(f"Error conectando a Jenkins: {e}", "danger")
        return redirect(url_for('test_bp.show_cycle', id=cycle_id))


    # Crumb
    crumb_field = None
    crumb_value = None
    try:
        crumb_resp = session.get(f"{JENKINS_URL}/crumbIssuer/api/json", timeout=10)
        if crumb_resp.status_code == 200:
            crumb_json = crumb_resp.json()
            crumb_field = crumb_json.get("crumbRequestField")
            crumb_value = crumb_json.get("crumb")
        else:
            flash(f"Error obteniendo crumb ({crumb_resp.status_code}).", "danger")
            return redirect(url_for('test_bp.show_cycle', id=cycle_id))
    except Exception as e:
        flash(f"Excepción al pedir crumb: {e}", "danger")
        return redirect(url_for('test_bp.show_cycle', id=cycle_id))

    headers = {}
    if crumb_field and crumb_value:
        headers[crumb_field] = crumb_value

    build_url = f"{JENKINS_URL}/job/{JOB}/buildWithParameters?token={TOKEN_BUILD}"

    enviados = 0

    # -----------------------------------
    # LANZAR TESTCASES con TEST_CYCLE_ID
    # -----------------------------------
    for tc in cycle.testcases:
        payload = {
            "TEST_SCRIPT": tc.test_script or "",
            "TEST_CASE_ID": str(tc.id),
            "TEST_CYCLE_ID": str(cycle_id),  # << AÑADIDO AQUÍ
            "ENTORNO": "staging",
            "USUARIO": "alex"
        }
        print("Payload enviado a Jenkins:", payload)
        
        try:
            resp = session.post(build_url, data=payload, headers=headers, timeout=15)

            if resp.status_code not in (200, 201, 202):
                print(f"❌ Error lanzando TC {tc.id}: {resp.status_code}, {resp.text[:200]}")
                continue

            enviados += 1
            print(f"✔ Lanzado TestCase {tc.id}")

        except Exception as ex:
            print(f"❌ Excepción enviando TC {tc.id}: {ex}")

    flash(f"Se han enviado {enviados} pruebas a Jenkins correctamente ✔", "success")
    return redirect(url_for('test_bp.show_cycle', id=cycle_id))



@automatizacion_bp.route("/api/results/from_jenkins/<int:test_case_id>", methods=["POST"])
def jenkins_callback(test_case_id):
    from flask import request
    from app.models.testcase_model import TestCase
    from app.models.result_model import Result, EstadoPruebaEnum
    from app import db
    import traceback, sys

    print(f"[CALLBACK] Recibido resultado para TestCase {test_case_id}", file=sys.stderr)

    try:
        test_case = TestCase.query.get(test_case_id)
        if not test_case:
            print(f"[ERROR] TestCase {test_case_id} no existe", file=sys.stderr)
            return {"error": "TestCase no encontrado"}, 404

        data = request.get_json()
        print("[CALLBACK] JSON recibido:", data, file=sys.stderr)

        if not data:
            return {"error": "No JSON recibido"}, 400

        estado = data.get("estado_prueba", "").upper()

        estado_map = {
            "PASADO": EstadoPruebaEnum.PASADO,
            "FALLIDO": EstadoPruebaEnum.FALLIDO,
            "BLOQUEADO": EstadoPruebaEnum.BLOQUEADO,
            "EN_PROGRESO": EstadoPruebaEnum.EN_PROGRESO
        }

        if estado not in estado_map:
            print(f"[ERROR] Estado inválido recibido: {estado}", file=sys.stderr)
            return {"error": "Estado inválido"}, 400

        # -----------------------------------
        # 1) Recoger el test_cycle_id SI VIENE
        # -----------------------------------
        cycle_id = data.get("test_cycle_id")  # puede venir None → perfecto

        nuevo_resultado = Result(
            test_case_id=test_case.id,
            estado_prueba=estado_map[estado],
            entorno="Automatizado",
            resultado_obtenido=data.get("resultado_obtenido", ""),
            notas=data.get("notas", ""),
            archivo=data.get("archivo"),
            test_cycle_id=cycle_id,   # ← lo guardamos solo si viene
            usu_created="Jenkins"
        )

        db.session.add(nuevo_resultado)
        db.session.commit()

        print("[CALLBACK] Resultado guardado correctamente", file=sys.stderr)

        return {"status": "OK"}, 200

    except Exception as e:
        print("[EXCEPTION]", e, file=sys.stderr)
        traceback.print_exc()
        return {"error": str(e)}, 500


# @automatizacion_bp.route("/api/results/from_jenkins/<int:test_case_id>", methods=["POST"])
# def jenkins_callback(test_case_id):
#     from flask import request
#     from app.models.testcase_model import TestCase
#     from app.models.result_model import Result, EstadoPruebaEnum
#     from app import db
#     import traceback

#     try:
#         test_case = TestCase.query.get_or_404(test_case_id)
#         data = request.get_json()
#         if not data:
#             return {"error": "No JSON recibido"}, 400

#         # Extraemos los campos del JSON
#         estado_prueba = data.get("estado_prueba", "")
#         resultado_obtenido = data.get("resultado_obtenido", "")
#         notas = data.get("notas", "")
#         archivo = data.get("archivo")

#         # Normalizamos el valor recibido para que coincida con tu enum
#         estado_map = {
#             "PASADO": EstadoPruebaEnum.PASADO,
#             "FALLIDO": EstadoPruebaEnum.FALLIDO,
#             "BLOQUEADO": EstadoPruebaEnum.BLOQUEADO,
#             "EN_PROGRESO": EstadoPruebaEnum.EN_PROGRESO
#         }

#         estado_prueba_enum = estado_map.get(estado_prueba.upper())
#         if not estado_prueba_enum:
#             return {"error": f"Estado no válido: {estado_prueba}"}, 400

#         # Creamos el resultado
#         nuevo_resultado = Result(
#             test_case_id=test_case.id,
#             estado_prueba=estado_prueba_enum,
#             entorno="Automatizado",
#             resultado_obtenido=resultado_obtenido,
#             notas=notas,
#             archivo=archivo,
#             usu_created="Jenkins"
#         )

#         db.session.add(nuevo_resultado)
#         db.session.commit()

#         return {"status": "OK"}, 200

#     except Exception as e:
#         # Para debug en consola de Flask
#         traceback.print_exc()
#         return {"error": str(e)}, 500



