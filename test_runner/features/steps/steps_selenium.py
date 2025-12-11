from behave import given, when, then 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys 
import time
@given('abro el navegador') 
def step_open_browser(context): 
    pass # Ya se abrió en environment.py 

@given('voy a la url "{url}"') 
@when('voy a la url "{url}"')
@then('voy a la url "{url}"') 
def step_go_to_url(context, url): 
    try: 
        context.driver.get(url) 
        time.sleep(1) 
        context.result["mensaje"] = f"Accedido a {url}" 
    except Exception as e: 
        context.result["estado"] = "FALLIDO" 
        context.result["mensaje"] = str(e) 
    
@when('escribo "{texto}" en el campo "{campo}"') 
def step_write_in_field(context, texto, campo): 
    try: 
        element = context.wait.until(lambda d: d.find_element(By.NAME, campo)) 
        element.clear() 
        element.send_keys(texto) 
    except Exception as e: 
        context.result["estado"] = "FALLIDO" 
        context.result["mensaje"] = f"No se pudo escribir en {campo}: {e}" 

@when('pulso ENTER en el campo "{campo}"') 
def step_press_enter(context, campo): 
    try: 
        element = context.wait.until(lambda d: d.find_element(By.NAME, campo)) 
        element.send_keys(Keys.RETURN) 
        time.sleep(1) 
    except Exception as e: 
        context.result["estado"] = "FALLIDO" 
        context.result["mensaje"] = f"No se pudo presionar ENTER en {campo}: {e}" 
        
@then('deberia ver el mensaje "{mensaje}"') 
def step_verify_message(context, mensaje): 
    # Solo un ejemplo, depende de cómo tu app muestre el mensaje 
    body_text = context.driver.find_element(By.TAG_NAME, "body").text 
    if mensaje in body_text: 
        context.result["estado"] = "PASADO" 
        context.result["mensaje"] = mensaje 
    else: 
        context.result["estado"] = "FALLIDO" 
        context.result["mensaje"] = f"No se encontró el mensaje: {mensaje}" 

@then('cierro el navegador mostrando "{mensaje}"') 
def step_close_browser(context, mensaje): 
    # Guardar el mensaje en el resultado 

    context.result["mensaje"] = mensaje 
    # Marcar como PASADO si no había fallos previos 

    if "estado" not in context.result or context.result["estado"] == "EN_PROGRESO": 
        context.result["estado"] = "PASADO" 
        try: 
            context.driver.quit() 
        except: 
            pass

@when('pulso el botón "{texto}"')
def step_click_button(context, texto):
    try:
        button = context.wait.until(
            lambda d: d.find_element(By.XPATH, f"//button[contains(text(), '{texto}')]")
        )
        button.click()
        time.sleep(1)
    except Exception as e:
        context.result["estado"] = "FALLIDO"
        context.result["mensaje"] = f"No pude pulsar el botón {texto}: {e}"

@then('deberia haber al menos {cantidad:d} productos en la página principal')
def step_count_products(context, cantidad):
    items = context.wait.until(
        lambda d: d.find_elements(By.CSS_SELECTOR, "#tbodyid .col-lg-4.col-md-6.mb-4")
    )
    assert len(items) >= cantidad, f"Solo se encontraron {len(items)} productos"

@then('cada producto debe mostrar nombre, imagen y precio')
def step_check_product_fields(context):
    items = context.driver.find_elements(By.CSS_SELECTOR, "#tbodyid .col-lg-4.col-md-6.mb-4")
    for item in items:
        item.find_element(By.TAG_NAME, "h4")  # nombre
        item.find_element(By.TAG_NAME, "img")  # imagen
        item.find_element(By.TAG_NAME, "h5")  # precio

@then('cada producto debe mostrar un nombre')
def step_check_product_name(context):
    items = context.driver.find_elements(By.CSS_SELECTOR, "#tbodyid .col-lg-4.col-md-6.mb-4")
    assert len(items) > 0, "No se encontraron productos"

    for item in items:
        name = item.find_element(By.TAG_NAME, "h4").text.strip()
        assert name != "", "Un producto no tenía nombre"


@then('cada producto debe mostrar una imagen')
def step_check_product_image(context):
    items = context.driver.find_elements(By.CSS_SELECTOR, "#tbodyid .col-lg-4.col-md-6.mb-4")
    assert len(items) > 0, "No se encontraron productos"

    for item in items:
        img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
        assert img and img.strip() != "", "Un producto no tenía imagen"


@then('cada producto debe mostrar un precio')
def step_check_product_price(context):
    items = context.driver.find_elements(By.CSS_SELECTOR, "#tbodyid .col-lg-4.col-md-6.mb-4")
    assert len(items) > 0, "No se encontraron productos"

    for item in items:
        price = item.find_element(By.TAG_NAME, "h5").text.strip()
        assert price != "", "Un producto no tenía precio"


@then('deberia estar en la página "{ruta}"')
def step_verify_url(context, ruta):
    assert ruta in context.driver.current_url, f"URL actual: {context.driver.current_url}"
