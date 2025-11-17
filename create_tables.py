# create_tables.py (versión corregida)
from app import create_app, db

# Importa clases y enums directamente desde los módulos (nombres según tú los llamaste)
from app.models.project_model import Project
from app.models.epic_hu_model import EpicHU, TipoEnum, PrioridadEnum, EstadoEnum
from app.models.testcase_model import TestCase
from app.models.testcycle_model import TestCycle
from app.models.result_model import Result
from app.models.epic_testcase_model import epic_testcase
from app.models.epic_testcycle_model import epic_testcycle
from app.models.testcase_testcycle_model import testcase_testcycle
from app.models.user_model import User, Role


app = create_app()

with app.app_context():
    db.create_all()

         # --- Crear roles base si no existen ---
    if not Role.query.first():
        print("Creando roles base...")
        admin_role = Role(nombre="admin", descripcion="Acceso completo al sistema")
        member_role = Role(nombre="miembro", descripcion="Puede crear y editar épicas, HUs, CTs, ciclos y defectos")
        viewer_role = Role(nombre="viewer", descripcion="Solo lectura")

        db.session.add_all([admin_role, member_role, viewer_role])
        db.session.commit()

        # --- Crear usuarios de prueba ---
        print("Creando usuarios de prueba...")

        admin = User(username="admin", email="admin@example.com")
        admin.set_password("admin123")
        admin.roles.append(admin_role)

        dev = User(username="devuser", email="dev@example.com")
        dev.set_password("dev123")
        dev.roles.append(member_role)

        viewer = User(username="viewer", email="viewer@example.com")
        viewer.set_password("viewer123")
        viewer.roles.append(viewer_role)

        db.session.add_all([admin, dev, viewer])
        db.session.commit()
        print("Usuarios de prueba creados correctamente.")


    # Solo insertar datos si no hay proyectos
    if not Project.query.first():
        print("Insertando datos de prueba...")

        # --- Crear proyectos (usa estados válidos definidos en Project) ---
        p1 = Project(nombre="Proyecto IA", descripcion="Sistema de IA para análisis de texto", estado="Activo", user_created=1)
        p2 = Project(nombre="App Móvil", descripcion="Aplicación Android de gestión", estado="Activo", user_created=1)

        db.session.add_all([p1, p2])
        db.session.commit()  # commit para tener IDs y objetos persistentes

        # --- Crear Epics / HU ---
        # puedes pasar el objeto proyecto=p1 o project_id=p1.id (ambos válidos)
        e1 = EpicHU(
            nombre="Módulo NLP",
            tipo=TipoEnum.EPIC,
            prioridad=PrioridadEnum.ALTA,
            descripcion="Desarrollar modelo de lenguaje",
            proyecto=p1,
            estado=EstadoEnum.NUEVO
        )

        e2= EpicHU(
            nombre="Front-End APP recetas",
            tipo=TipoEnum.EPIC,
            prioridad=PrioridadEnum.MEDIA,
            descripcion="Crear endpoint REST",
            proyecto=p2,
            estado=EstadoEnum.NUEVO
        )
        e3 = EpicHU(
            nombre="Back-End APP recetas",
            tipo=TipoEnum.EPIC,
            prioridad=PrioridadEnum.MEDIA,
            descripcion="En esta epica de deberemos crear: La BBDD, la receta_Activity y los ingredientes_Activity",
            proyecto=p2,
            estado=EstadoEnum.NUEVO
        )

        db.session.add_all([e1, e2, e3])
        db.session.commit()

        e4 = EpicHU(
            nombre="UI de Login",
            tipo=TipoEnum.HU,
            prioridad=PrioridadEnum.MEDIA,
            descripcion="Pantalla de login y registro",
            epica_id=e2.id,
            proyecto=p2,
            estado=EstadoEnum.EN_PROGRESO
        )
        e5 = EpicHU(
            nombre="Vistas de recetas y blog",
            tipo=TipoEnum.HU,
            prioridad=PrioridadEnum.MEDIA,
            descripcion="Crear con xml las vistas ",
            epica_id=e2.id,
            proyecto=p2,
            estado=EstadoEnum.NUEVO
        )
        e6 = EpicHU(
            nombre="Creacion BBDD APP recetas",
            tipo=TipoEnum.EPIC,
            prioridad=PrioridadEnum.MEDIA,
            descripcion="Crear la base de datos con los siguientes tablas: recetas, ingredientes, rectas_ingredientes, etc",
            epica_id=e3.id,
            proyecto=p2,
            estado=EstadoEnum.TERMINADO
        )

        e7 = EpicHU(
            nombre="Creacion RecetaActivity",
            tipo=TipoEnum.HU,
            prioridad=PrioridadEnum.MEDIA,
            descripcion="Crear el controlador que saque toda la informacion de tabla recetas",
            epica_id=e3.id,
            proyecto=p2,
            estado=EstadoEnum.EN_PROGRESO
        )

        e8 = EpicHU(
            nombre="Creacion IngredientesActivity",
            tipo=TipoEnum.HU,
            prioridad=PrioridadEnum.MEDIA,
            descripcion="Crear el controlador que saque toda la informacion de tabla ingredientes",
            epica_id=e3.id,
            proyecto=p2,
            estado=EstadoEnum.NUEVO
        )

        db.session.add_all([e1, e2, e3, e4, e5, e6, e7, e8])
        db.session.commit()


        # --- Crear Test Cases ---
        t1 = TestCase(nombre="Test de autenticación", objetivo="Verifica login correcto")
        t2 = TestCase(nombre="Test de API NLP", objetivo="Comprueba respuesta JSON del modelo")
        t3 = TestCase(nombre="Test visual de interfaz", objetivo="Comprueba diseño responsivo")

        db.session.add_all([t1, t2, t3])
        db.session.commit()

        # --- Crear Test Cycles ---
        c1 = TestCycle(nombre="Sprint 1", descripcion="Primera ronda de pruebas del proyecto IA")
        c2 = TestCycle(nombre="Sprint 2", descripcion="Segunda ronda de pruebas del proyecto móvil")

        db.session.add_all([c1, c2])
        db.session.commit()

        # --- Asociaciones (tablas N:M) ---
        # Insertamos en las tablas intermedias usando .insert()
        db.session.execute(testcase_testcycle.insert().values(testcase_id=t1.id, testcycle_id=c1.id))
        db.session.execute(testcase_testcycle.insert().values(testcase_id=t2.id, testcycle_id=c1.id))
        db.session.execute(testcase_testcycle.insert().values(testcase_id=t3.id, testcycle_id=c2.id))

        db.session.execute(epic_testcase.insert().values(epic_id=e1.id, testcase_id=t1.id))
        db.session.execute(epic_testcycle.insert().values(epic_id=e1.id, testcycle_id=c1.id))
        db.session.execute(epic_testcase.insert().values(epic_id=e3.id, testcase_id=t3.id))

        db.session.commit()
        print("Datos de prueba insertados correctamente.")
    else:
        print("La base de datos ya contiene datos, no se insertó nada nuevo.")


