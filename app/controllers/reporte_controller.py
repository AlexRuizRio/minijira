
from flask import Blueprint, send_file, jsonify
from app import db
from app.models.testcase_model import TestCase, EstadoEnum
from app.models.testcycle_model import TestCycle, EstadoEnum
from app.models.result_model import Result, EstadoPruebaEnum
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from openpyxl import Workbook

reporte_bp = Blueprint("reporte", __name__, url_prefix="/reporte")

def get_test_cycle_report(test_cycle_id):
    cycle = TestCycle.query.filter_by(id=test_cycle_id).first()
    if not cycle:
        return None

    report = {
        "id": cycle.id,
        "nombre": cycle.nombre,
        "descripcion": cycle.descripcion,
        "estado": cycle.estado.value,
        "testcases": [],
        "stats": {
            "total_tc": 0,
            "total_results": 0,
            "pasados": 0,
            "fallidos": 0,
            "bloqueados": 0,
            "en_progreso": 0,
            "defectos": {
                "abiertos": 0,
                "en_progreso": 0,
                "cerrados": 0
            }
        }
    }

    estado_defecto_map = {
        "abierto": "abiertos",
        "cerrado": "cerrados",
        "en progreso": "en_progreso"
    }

    estado_result_map = {
        "pasado": "pasados",
        "fallido": "fallidos",
        "bloqueado": "bloqueados",
        "en_progreso": "en_progreso"
    }

    for tc in cycle.testcases:
        result = Result.query.filter_by(
            test_cycle_id=test_cycle_id,
            test_case_id=tc.id
        ).order_by(Result.fecha_created.desc()).first()

        defects = []
        all_defects = list(tc.defects) + ([result.defects] if result else [])

        for d in tc.defects:
            defects.append({
                "id": d.id,
                "titulo": d.titulo,
                "estado": d.estado,
                "prioridad": d.prioridad,
                "verificado": d.verificado
            })
            key = estado_defecto_map.get(d.estado.lower(), "abiertos")
            report["stats"]["defectos"][key] += 1

        if result:
            key = estado_result_map.get(result.estado_prueba.value, "en_progreso")
            report["stats"][key] += 1

        report["stats"]["total_tc"] += 1
        if result:
            report["stats"]["total_results"] += 1

        report["testcases"].append({
            "id": tc.id,
            "nombre": tc.nombre,
            "objetivo": tc.objetivo,
            "prioridad": tc.prioridad.value if tc.prioridad else None,
            "tipo": tc.tipo.value if tc.tipo else None,
            "estado_tc": tc.estado.value if tc.estado else None,
            "result": {
                "estado": result.estado_prueba.value if result else None,
                "notas": result.notas if result else None,
                "entorno": result.entorno if result else None,
                "fecha": result.fecha_created if result else None,
                "resultado_obtenido": result.resultado_obtenido if result else None,
            },
            "defectos": defects
        })

    return report



@reporte_bp.route("/testcycle/<int:test_cycle_id>/excel")
def descargar_reporte_excel(test_cycle_id):
    report = get_test_cycle_report(test_cycle_id)

    if not report:
        return jsonify({"error": "Test cycle no encontrado"}), 404

    wb = Workbook()
    ws = wb.active
    ws.title = "Resumen"

    ws.append(["Campo", "Valor"])
    ws.append(["Nombre", report["nombre"]])
    ws.append(["Descripción", report["descripcion"]])
    ws.append(["Estado", report["estado"]])

    ws_tc = wb.create_sheet("TestCases")
    ws_tc.append(["ID", "Nombre", "Estado", "Resultado", "Notas"])

    for tc in report["testcases"]:
        ws_tc.append([
            tc["id"],
            tc["nombre"],
            tc["estado_tc"],
            tc["result"]["estado"],
            tc["result"]["notas"]
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        download_name=f"reporte_testcycle_{test_cycle_id}.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@reporte_bp.route("/testcycle/<int:test_cycle_id>/pdf")
def descargar_reporte_pdf(test_cycle_id):
    report = get_test_cycle_report(test_cycle_id)
    if not report:
        return jsonify({"error": "Test cycle no encontrado"}), 404

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    # --- Cabecera ---
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, f"Reporte Test Cycle: {report['nombre']}")
    y -= 25
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Descripción: {report['descripcion'] or 'Sin descripción'}")
    y -= 20
    pdf.drawString(50, y, f"Estado: {report['estado']}")
    y -= 30

    # --- Resumen estadístico ---
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Resumen:")
    y -= 20
    pdf.setFont("Helvetica", 12)

    stats = report["stats"]
    # Resultados
    for estado in ["pasados", "fallidos", "bloqueados", "en_progreso"]:
        color_map = {
            "pasados": (0, 0.6, 0),  # verde
            "fallidos": (1, 0, 0),   # rojo
            "bloqueados": (1, 0.65, 0), # naranja
            "en_progreso": (0.5, 0.5, 0.5) # gris
        }
        pdf.setFillColorRGB(*color_map[estado])
        pdf.drawString(70, y, f"{estado.capitalize()}: {stats[estado]}")
        y -= 15
    pdf.setFillColorRGB(0, 0, 0)
    # Defectos
    pdf.drawString(50, y, "Defectos:")
    y -= 15
    for key, value in stats["defectos"].items():
        pdf.drawString(70, y, f"{key.capitalize()}: {value}")
        y -= 15

    y -= 10
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "TestCases:")
    y -= 20
    pdf.setFont("Helvetica", 10)

    # --- Tabla de TestCases ---
    row_height = 15
    for tc in report["testcases"]:
        if y < 80:  # nueva página si falta espacio
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

        # Nombre + Tipo + Prioridad + Estado
        estado_result = tc["result"]["estado"] or "Sin ejecutar"
        color_map = {
            "pasado": (0, 0.6, 0),
            "fallido": (1, 0, 0),
            "bloqueado": (1, 0.65, 0),
            "en_progreso": (0.5, 0.5, 0.5),
            None: (0, 0, 0)
        }
        pdf.setFillColorRGB(*color_map.get(estado_result, (0, 0, 0)))

        pdf.drawString(50, y, f"{tc['nombre']} ({tc['tipo'] or '-'}) [{tc['prioridad'] or '-'}]")
        pdf.drawString(350, y, f"Estado: {tc['estado_tc'] or '-'}")
        pdf.drawString(470, y, f"Resultado: {estado_result}")
        y -= row_height

        # Notas si existen
        notas = tc["result"]["notas"]
        if notas:
            for line in notas.splitlines():
                pdf.setFillColorRGB(0, 0, 0)
                pdf.drawString(60, y, f"Notas: {line}")
                y -= row_height
                if y < 80:
                    pdf.showPage()
                    y = height - 50
                    pdf.setFont("Helvetica", 10)

        # Defectos
        for d in tc["defectos"]:
            pdf.setFillColorRGB(0.6, 0, 0.6)  # morado para defectos
            pdf.drawString(60, y, f"Defecto: {d['titulo']} [{d['estado']}] Prioridad: {d['prioridad']}")
            y -= row_height
            if y < 80:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"reporte_testcycle_{test_cycle_id}.pdf",
        mimetype="application/pdf"
    )
