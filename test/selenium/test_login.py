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
        log = "Error: Al encontrar username"
        time.sleep(2)
        username = wait.until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        log = "Error: Al encontrar password"
        password = driver.find_element(By.NAME, "password")

        log = "Error: Al insertar el username"
        username.send_keys("admin")
        time.sleep(1)
        log = "Error: Al insertar el password"
        password.send_keys("admin123")

        time.sleep(1)
        
        password.send_keys(Keys.RETURN)

        time.sleep(2)
    except ErrorLoginException:
        print(log)
    finally:
        print("OK")
        driver.quit()

if __name__ == "__main__":
    main()