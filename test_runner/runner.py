import json, os, re, sys, subprocess, traceback, uuid

def run_feature(feature_path):
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # test_runner/
        FEATURES_DIR = os.path.join(BASE_DIR, "features")
        RESULTS_DIR = os.path.join(BASE_DIR, "results")

        os.makedirs(RESULTS_DIR, exist_ok=True)

        # Siempre usar el feature dentro de /features/
        feature_name = os.path.basename(feature_path)
        feature_abs = os.path.join(FEATURES_DIR, feature_name)

        if not os.path.exists(feature_abs):
            raise FileNotFoundError(f"Feature no encontrado en: {feature_abs}")

        # Ruta relativa para behave
        feature_rel = os.path.relpath(feature_abs, BASE_DIR)

        # result.json único por ejecución para evitar conflictos
        run_id = uuid.uuid4().hex[:8]
        result_json_path = os.path.join(RESULTS_DIR, f"result_{run_id}.json")

        proc = subprocess.run(
            [
                sys.executable,
                "-m", "behave",
                feature_rel,
                "-f", "json",
                "-o", result_json_path
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        behave_stdout = proc.stdout
        behave_stderr = proc.stderr

        if not os.path.exists(result_json_path):
            output_json = {
                "estado_prueba": "FALLIDO",
                "resultado_obtenido": "Behave no generó result.json",
                "notas": f"STDOUT:\n{behave_stdout}\n\nSTDERR:\n{behave_stderr}",
                "archivo": None
            }
            print(json.dumps(output_json))
            return

        with open(result_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        feature = data[0]

        for escenario in feature["elements"]:
            steps = escenario.get("steps", [])
            todos_pasaron = all(s.get("result", {}).get("status") == "passed" for s in steps)
            estado = "PASADO" if todos_pasaron else "FALLIDO"

            # Último step seguro
            ultimo_step = steps[-1] if steps else {}
            match = re.search(r'"(.*?)"', ultimo_step.get("name", ""))
            resultado_obtenido = match.group(1) if match else ultimo_step.get("name", "")

            notas = f"Feature: {feature.get('name','')}\n"
            for s in steps:
                keyword = s.get("keyword", "")
                name = s.get("name", "")
                status = s.get("result", {}).get("status", "SKIPPED")  # fallback seguro
                notas += f"{keyword} {name}  → {status}\n"

            archivo = escenario.get("evidencia") or None

            output_json = {
                "estado_prueba": estado,
                "resultado_obtenido": resultado_obtenido,
                "notas": notas,
                "archivo": archivo
            }

            print(json.dumps(output_json))

        # Limpieza segura
        try:
            os.remove(result_json_path)
        except:
            pass

    except Exception:
        fallback = {
            "estado_prueba": "FALLIDO",
            "resultado_obtenido": "Error interno en runner.py",
            "notas": traceback.format_exc(),
            "archivo": None
        }
        print(json.dumps(fallback))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "estado_prueba": "FALLIDO",
            "resultado_obtenido": "No se pasó la ruta del feature",
            "notas": "runner.py requiere el .feature como parámetro",
            "archivo": None
        }))
    else:
        run_feature(sys.argv[1])
