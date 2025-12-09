from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# Driver global por escenario
def before_scenario(context, scenario):
    context.driver = webdriver.Chrome()
    context.wait = WebDriverWait(context.driver, 5)
    context.log = ""


def after_scenario(context, scenario):
    try:
        context.driver.quit()
    except:
        pass


@given('abro el navegador')
def step_open_browser(context):
    # Ya se abrió en before_scenario, pero mantenemos el step por semántica
    pass


@given('voy a la url "{url}"')
def step_go_to_url(context, url):
    context.log = "Error: No se pudo acceder a la URL"
    context.driver.get(url)
    time.sleep(1)


@when('escribo "{texto}" en el campo "{campo}"')
def step_write_in_field(context, texto, campo):
    context.log = f"Error: No se encontró el campo {campo}"
    element = context.wait.until(EC.element_to_be_clickable((By.NAME, campo)))
    context.log = f"Error: No se pudo escribir en {campo}"
    element.send_keys(texto)
    time.sleep(1)


@when('pulso ENTER en el campo "{campo}"')
def step_press_enter(context, campo):
    context.log = f"Error: No se encontró el campo {campo} para ENTER"
    element = context.wait.until(EC.presence_of_element_located((By.NAME, campo)))
    element.send_keys(Keys.RETURN)
    time.sleep(1)


@then('cierro el navegador mostrando "{mensaje}"')
def step_close_browser(context, mensaje):
    print(f"RESULTADO_FINAL: {mensaje}")
    context.driver.quit()

