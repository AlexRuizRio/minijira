from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def main():
    driver = webdriver.Chrome()

    try:
        log = "Error: En el driver"

        driver.get("http://127.0.0.1:5000/login")

        wait = WebDriverWait(driver, 3)

        log = "Error: En el login"
        username = wait.until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )

        password = driver.find_element(By.NAME, "password")

        username.send_keys("admin")
        password.send_keys("admin123")

        time.sleep(1)
        
        password.send_keys(Keys.RETURN)
        time.sleep(2)

        #CREAR
        log = "Error: En el boton create"
        boton = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/main/a"))
        )
        boton.click()
        time.sleep(3)

        log = "Error: En el campo nombre"
        nombre = wait.until(
            EC.element_to_be_clickable((By.NAME, "nombre"))
        )

        log = "Error: En el campo descripcion"
        descripcion = driver.find_element(By.NAME, "descripcion")

        log = "Error: Al enviar los datos"
        nombre.send_keys("Proy Selenium")
        descripcion.send_keys("Esto es un proyecto creado a traves de Selenium")

        log = "Error: Al enviar los datos"
        boton = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div/div/div/form/button"))
        )
        boton.click()
        time.sleep(2)
        
        print("OK")
    except Exception:
        print(log)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()