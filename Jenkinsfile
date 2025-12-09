import groovy.json.JsonSlurper
import groovy.json.JsonOutput

// ----------------------
// parseJsonSafe -> devuelve un java.util.HashMap (serializable)
// ----------------------
@NonCPS
Map parseJsonSafe(String json) {
    def parsed = new JsonSlurper().parseText(json)
    if (parsed instanceof Map) {
        return new HashMap(parsed)   // convierte LazyMap -> HashMap (serializable)
    }
    return parsed
}

pipeline {
    agent any

    environment {
        BASE_PATH   = "C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\Pipeline\\test_runner"
        PYTHON_PATH = "C:\\Users\\ardelrio\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" // Ajusta si hace falta
    }

    parameters {
        string(name: 'TEST_SCRIPT',   defaultValue: '', description: 'Contenido Gherkin (individual)')
        string(name: 'TEST_CASE_ID',  defaultValue: '', description: 'ID individual')
        string(name: 'TEST_CASE_IDS', defaultValue: '', description: 'JSON list: [1,2,3] or comma list')
        string(name: 'TEST_CYCLE_ID', defaultValue: '', description: 'ID del ciclo (opcional)')
    }

    stages {
        stage('Preparar workspace') {
            steps {
                script {
                    echo "Usando repo en: ${BASE_PATH}"
                    def runnerPath = "${BASE_PATH}\\runner.py"
                    if (!fileExists(runnerPath)) {
                        error "runner.py NO encontrado en ${runnerPath}"
                    }
                    if (!fileExists("${PYTHON_PATH}")) {
                        // No buscamos "python" en PATH (evita ambigüedades). Si no está, damos info.
                        echo "Advertencia: no se encontró el ejecutable en PYTHON_PATH: ${PYTHON_PATH}"
                        // opcional: error si quieres forzar
                        // error "Python no encontrado en PYTHON_PATH"
                    }
                    echo "✔ runner.py OK"
                }
            }
        }

        stage('Detectar modo') {
            steps {
                script {
                    if (params.TEST_CASE_IDS?.trim()) {
                        echo "Modo CICLO detectado → ${params.TEST_CASE_IDS}"
                    } else {
                        echo "Modo INDIVIDUAL detectado"
                    }
                }
            }
        }

        stage('Ejecutar Tests') {
            steps {
                script {
                    // -------------------------------------------------------
                    // Función que ejecuta 1 test (puede generar N JSON si hay Outline)
                    // -------------------------------------------------------
                    def ejecutarUna = { testId, gherkinContent ->
                        def timestamp = System.currentTimeMillis()
                        def featureName = "temp_${testId}_${timestamp}.feature"
                        def featurePath = "${BASE_PATH}\\features\\${featureName}"

                        // --- Crear feature ---
                        if (gherkinContent?.trim()) {
                            writeFile file: featurePath, text: gherkinContent
                        } else {
                            def baseTemp = "${BASE_PATH}\\features\\temp.feature"
                            if (!fileExists(baseTemp)) {
                                error("No existe ${baseTemp} y no se pasó TEST_SCRIPT")
                            }
                            // copy preservando CRLF en Windows
                            bat script: "copy /Y \"${baseTemp}\" \"${featurePath}\""
                        }

                        // --- Ejecutar runner.py (desde BASE_PATH) ---
                        def cmd = "\"${PYTHON_PATH}\" \"${BASE_PATH}\\runner.py\" \"${featurePath}\" ${testId}"
                        echo "Run cmd: ${cmd}"

                        def raw = bat(
                            label: "Run Test ${testId}",
                            script: cmd,
                            returnStdout: true
                        ).trim()

                        echo "Salida raw:"
                        echo raw

                        // --- Capturar todas las líneas JSON válidas ---
                        def jsonLines = []
                        raw.readLines().each { line ->
                            def l = line.trim()
                            if (l.startsWith("{") && l.endsWith("}")) {
                                jsonLines << l
                            }
                        }

                        if (jsonLines.isEmpty()) {
                            error("❌ No se detectó JSON válido en la salida del runner.\nSalida completa:\n${raw}")
                        }

                        echo "✔ Detectados ${jsonLines.size()} resultado(s) JSON para Test ${testId}"

                        // --- Enviar cada JSON al backend (uno por escenario) ---
                        jsonLines.each { jsonLinea ->
                            // convertir a HashMap serializable
                            def jsonObj = parseJsonSafe(jsonLinea)

                            // si venimos de un ciclo, añadir test_cycle_id
                            if (params.TEST_CYCLE_ID?.trim()) {
                                jsonObj["test_cycle_id"] = params.TEST_CYCLE_ID
                            }

                            def body = JsonOutput.toJson(jsonObj)

                            // POST
                            def url = "http://localhost:5000/automatizacion/api/results/from_jenkins/${testId}"
                            echo "POST -> ${url} (payload size: ${body.size()})"
                            try {
                                httpRequest(
                                    httpMode: 'POST',
                                    url: url,
                                    contentType: 'APPLICATION_JSON',
                                    requestBody: body,
                                    validResponseCodes: "100:399"
                                )
                            } catch (err) {
                                // no petamos todo el pipeline por un envío fallido, pero lo informamos
                                echo "❌ Error al enviar resultado para ${testId}: ${err}"
                            }
                        } // end each jsonLinea
                    } // end ejecutarUna

                    // -------------------------------------------------------
                    // Lógica principal: si PASAN TEST_CASE_IDS -> ciclo, si no -> individual
                    // -------------------------------------------------------
                    if (params.TEST_CASE_IDS?.trim()) {
                        // intentar parsear JSON array, si falla llamar a split
                        def ids = null
                        try {
                            ids = new JsonSlurper().parseText(params.TEST_CASE_IDS)
                        } catch (e) {
                            // fallback: "1,2,3"
                            ids = []
                            params.TEST_CASE_IDS.split(",").each { ids << it.trim() }
                        }

                        // for normal (evitamos operadores no soportados)
                        for (def i = 0; i < ids.size(); i++) {
                            def idVal = ids[i].toString()
                            ejecutarUna(idVal, "")   // contenido vacío -> el runner copiará temp.feature base
                        }
                    } else {
                        if (!params.TEST_CASE_ID?.trim()) {
                            error("Debes pasar TEST_CASE_ID o TEST_CASE_IDS")
                        }
                        ejecutarUna(params.TEST_CASE_ID, params.TEST_SCRIPT)
                    }

                } // end script
            } // end steps
        } // end stage Ejecutar Tests
    } // end stages

    post {
        always {
            echo "Pipeline finalizado"
        }
    }
}
