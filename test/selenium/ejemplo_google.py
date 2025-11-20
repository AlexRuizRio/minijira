from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def main():
    driver = webdriver.Chrome()

    try:
        driver.get("http://127.0.0.1:5000/login")

        wait = WebDriverWait(driver, 3)

        username = wait.until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )

        password = driver.find_element(By.NAME, "password")

        username.send_keys("admin")
        password.send_keys("admin123")

        time.sleep(1)
        
        password.send_keys(Keys.RETURN)
        time.sleep(2)

        boton = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/main/a"))
        )
        boton.click()
        time.sleep(3)

        #CREAR
        nombre = wait.until(
            EC.element_to_be_clickable((By.NAME, "nombre"))
        )

        descripcion = driver.find_element(By.NAME, "descripcion")

        nombre.send_keys("Proy Selenium")
        descripcion.send_keys("Esto es un proyecto creado a traves de Selenium")

        boton = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div/div/div/form/button"))
        )
        boton.click()
        time.sleep(2)

        boton = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/a[2]"))
        )
        boton.click()
        time.sleep(2)


        # EDITAR
        boton = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/main/div[1]/a[1]"))
        )
        boton.click()

        nombre = wait.until(
            EC.element_to_be_clickable((By.NAME, "nombre"))
        )

        descripcion = driver.find_element(By.NAME, "descripcion")
        nombre.clear()
        descripcion.clear()

        time.sleep(1)

        nombre.send_keys("Cambio de nombre")
        descripcion.send_keys("Cambio de descripcion")

        boton = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div/div/div/form/button"))
        )
        boton.click()
        time.sleep(2)


        # BORRAR
        boton = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/main/div[1]/a[2]"))
        )
        boton.click()
        time.sleep(2)
        
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except NoAlertPresentException:
            print("No hay alert abierto")
        time.sleep(2)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
