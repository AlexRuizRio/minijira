import os, time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

UPLOAD_DIR = r"C:\Users\ardelrio\EjerciciosPython\minijira\uploads"

def before_scenario(context, scenario):
    # Inicializamos evidencia
    context.evidencia_path = None

    # Opciones de Chrome (manteniendo lo que tenías)
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    # Inicializamos driver
    context.driver = webdriver.Chrome(options=options)

    # Espera implícita y explícita
    context.driver.implicitly_wait(5)
    context.wait = WebDriverWait(context.driver, 5)

    # Inicializamos resultado por escenario
    context.result = {
        "estado": "EN_PROGRESO",
        "mensaje": ""
    }

    # Pequeña pausa para evitar fallos en arranque en frío
    time.sleep(0.4)

def after_step(context, step):
    # Captura evidencia solo si falla
    if step.status == "failed":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evidencia_fail_{timestamp}.png"
        full_path = os.path.join(UPLOAD_DIR, filename)
        try:
            context.driver.save_screenshot(full_path)
            context.evidencia_path = filename
        except:
            context.evidencia_path = None

def after_scenario(context, scenario):
    # Cierra el navegador al final de cada escenario
    try:
        context.driver.quit()
    except:
        pass
