import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.detalle_proyecto_page import DetalleProyectoPage
from pages.nuevo_proyecto_page import NuevoProyectoPage

@pytest.mark.selenium
def test_crear_y_ver_detalle_proyecto(driver):
    # 1️⃣ Login
    login = LoginPage(driver)
    login.load()
    login.login("admin", "admin123")

    # 2️⃣ Ir al dashboard
    dash = DashboardPage(driver)
    dash.load()

    # 3️⃣ Crear proyecto
    dash.click_crear_proyecto()
    nuevo = NuevoProyectoPage(driver)
    nuevo.rellenar_formulario("Proyecto Selenium", "Descripción Selenium")

    # 4️⃣ Volver al dashboard y click en el proyecto
    dash.load()
    assert dash.click_proyecto("Proyecto Selenium"), "No se encontró el proyecto en el dashboard"

    # 5️⃣ Verificar detalle del proyecto
    detalle = DetalleProyectoPage(driver)
    assert detalle.en_pagina_detalle(), "No se abrió la página de detalle"
    assert detalle.get_titulo() == "Proyecto Selenium"
