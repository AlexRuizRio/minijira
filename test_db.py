from app import create_app, db
from app.models import EpicHU, TestCase

app = create_app()

with app.app_context():
    # Crear un Epic de prueba
    epic = EpicHU(nombre="Epic de prueba", tipo="Feature", prioridad="Alta", estado="Abierto")
    db.session.add(epic)
    db.session.commit()
    print("Epic creado con id:", epic.id)

    # Crear un TestCase de prueba
    tc = TestCase(nombre="Test de prueba", estado="Pendiente", prioridad="Alta", tipo="Manual")
    db.session.add(tc)
    db.session.commit()
    print("TestCase creado con id:", tc.id)
