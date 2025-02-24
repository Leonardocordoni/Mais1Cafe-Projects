import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import pyperclip
import time
from selenium.webdriver.common.keys import Keys


planilha = pd.read_excel('Excel local')


driver = ('Drive local')

chrome_options = Options()
chrome_options.add_argument("--start-maximized")


service = Service(driver)
driver = webdriver.Chrome(service=service, options=chrome_options)


driver.get('https://login.contaazul.com/#/')  


time.sleep(3)


usuario_input = driver.find_element(By.XPATH, "//input[@type='email']")  
usuario_input.send_keys('email')

senha_input = driver.find_element(By.XPATH, "//input[@type='password']")  
senha_input.send_keys('senha')
senha_input.send_keys(Keys.RETURN)  


time.sleep(15)


driver.get('https://app.contaazul.com/#/ca/financeiro/contas-a-receber')  


time.sleep(15) # tempo para colocar os filtros manualmente

while True:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@data-v-13d60518 and contains(text(), 'Ações') and not(contains(text(), 'lote'))]"))
    ).click()


       
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@data-v-85c9500b and contains(text(), 'Editar lançamento')]"))
    ).click()

    time.sleep(3)


    description_field = driver.find_element(By.XPATH, "//label[span[contains(text(), 'Descrição')]]//following-sibling::div//input[@class='ds-input ds-form-control']")
    description_field.click()
    description_field.send_keys(Keys.CONTROL, 'a')
    description_field.send_keys(Keys.BACKSPACE)
    pyperclip.copy('Royalties Janeiro')
    description_field.click()
    description_field.send_keys(Keys.CONTROL, 'v')

    time.sleep(1)

    button = driver.find_element(By.XPATH, "//div[@class='ds-footer ds-rollover-footer' and @data-v-8c16e35d]//div[@class='ds-footer__content ds-u-display--flex ds-u-justify-content--space-between']//button[@class='ds-loader-button__button ds-button ds-button-primary ds-button-md']")
    driver.execute_script("arguments[0].click();", button)

    time.sleep(3) 

