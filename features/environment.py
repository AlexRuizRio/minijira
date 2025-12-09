from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

def before_scenario(context, scenario):
    context.driver = webdriver.Chrome()
    context.wait = WebDriverWait(context.driver, 5)
    context.log = ""

def after_scenario(context, scenario):
    try:
        context.driver.quit()
    except:
        pass
