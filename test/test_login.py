import pytest
import time
from test.pages.login_page import LoginPage

@pytest.mark.login
@pytest.mark.selenium
def test_login_correcto(driver):
    page = LoginPage(driver)
    page.load()
    page.login("admin", "admin123")

    time.sleep(2)  # SOLO PARA DEBUG

    print("DEBUG URL:", driver.current_url)

    assert page.is_logged_in(), "Login correcto pero no se detecta página de proyectos."


@pytest.mark.login
@pytest.mark.selenium
def test_login_incorrecto(driver):
    page = LoginPage(driver)
    page.load()
    page.login("admin", "wrongpassword")
    # como no hay flash, verificamos que sigue en login
    assert "login" in page.driver.current_url.lower(), "El login fallido debería quedarse en la página de login"
