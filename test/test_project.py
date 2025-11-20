import pytest
from app.models.project_model import Project
from app.models.epic_hu_model import EpicHU, TipoEnum
from app import db


# ============================================
# Helper: login directo como ADMIN ya existente
# ============================================
def login_admin(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["roles"] = ["admin"]
        sess["username"] = "admin"


# =============================================================
# 1) INDEX - requiere login
# =============================================================
def test_index_requires_login(client):
    response = client.get("/proyectos/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.location


def test_index_logged_in(client):
    login_admin(client)

    response = client.get("/proyectos/")
    assert response.status_code == 200


# =============================================================
# 2) INDEX - muestra proyectos
# =============================================================
def test_index_shows_projects(app, client):
    login_admin(client)

    with app.app_context():
        p = Project(nombre="Proyecto Test", descripcion="Demo", user_created=1)
        db.session.add(p)
        db.session.commit()

    response = client.get("/proyectos/")
    assert b"Proyecto Test" in response.data


# =============================================================
# 3) DETALLE PROYECTO
# =============================================================
def test_detalle_proyecto(app, client):
    from app.models.epic_hu_model import EpicHU, TipoEnum

    login_admin(client)

    with app.app_context():
        # Crear proyecto
        p = Project(nombre="Proyecto Detalle", descripcion="Demo", user_created=1)
        db.session.add(p)
        db.session.commit()

        # Crear épica + HU con el argumento correcto 'proyecto_id'
        epic = EpicHU(nombre="Epic 1", tipo=TipoEnum.EPIC, proyecto_id=p.id)
        db.session.add(epic)
        db.session.commit()

        # HU hija de la épica
        hu = EpicHU(nombre="HU 1", tipo=TipoEnum.HU, proyecto_id=p.id, epica_id=epic.id)
        db.session.add(hu)
        db.session.commit()

    response = client.get(f"/proyectos/proyecto/{p.id}")
    assert response.status_code == 200
    assert b"Proyecto Detalle" in response.data
    assert b"Epic 1" in response.data
    assert b"HU 1" in response.data


# =============================================================
# 4) CREAR PROYECTO
# =============================================================
def test_crear_proyecto(client):
    login_admin(client)

    # Mandar POST con user_created ya que es obligatorio
    response = client.post(
        "/proyectos/proyecto/nuevo",
        data={"nombre": "Nuevo Proyecto", "descripcion": "Desc"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Nuevo Proyecto" in response.data

# =============================================================
# 5) EDITAR PROYECTO
# =============================================================
def test_editar_proyecto(app, client):
    login_admin(client)

    with app.app_context():
        p = Project(nombre="Viejo", descripcion="Vieja desc", user_created=1)
        db.session.add(p)
        db.session.commit()
        pid = p.id

    response = client.post(
        f"/proyectos/proyecto/{pid}/editar",
        data={"nombre": "Nuevo Nombre", "descripcion": "Nueva Desc"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Nuevo Nombre" in response.data


# =============================================================
# 6) ELIMINAR PROYECTO
# =============================================================
def test_eliminar_proyecto(app, client):
    login_admin(client)

    with app.app_context():
        p = Project(nombre="Proyecto a borrar", descripcion="xxx", user_created=1)
        db.session.add(p)
        db.session.commit()
        pid = p.id

    response = client.get(
        f"/proyectos/proyecto/{pid}/eliminar",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Proyecto a borrar" not in response.data
