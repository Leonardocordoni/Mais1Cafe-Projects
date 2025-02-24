import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

planilha = pd.read_excel('Excel Local')

driver = ('Driver Local')

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

service = Service(driver)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://sistema.mais1cafe.com.br/login')

time.sleep(3)

usuario_input = driver.find_element(By.NAME, 'username')
usuario_input.send_keys('Name')

senha_input = driver.find_element(By.NAME, 'password')
senha_input.send_keys('password')

senha_input.send_keys(Keys.RETURN)

time.sleep(5)

driver.get('https://sistema.mais1cafe.com.br/financeiro/lista/1?companyId=')

time.sleep(5)

for index, row in planilha.iterrows():
    
    add_button = driver.find_element(By.XPATH, "//button[@data-tour-id='button_create_top']")
    add_button.click()

    time.sleep(3)

    descricao_input = driver.find_element(By.NAME, 'description')
    descricao_input.send_keys(row['Descrição'])

    valor_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Valor *']")
    valor = row['Valor']

    valor_formatado = str(valor).replace('.', ',')

    for digit in valor_formatado:
        valor_input.send_keys(digit)

    valor_L_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Valor Líquido *']")
    valor = row['Valor_L']

    valor_formatado_liquido = str(valor).replace('.', ',')

    for digit_L in valor_formatado_liquido:
        valor_L_input.send_keys(digit_L)

    Due_date = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='dd/mm/aaaa'][title='N/A']")))
    
    Due_date.click()
    
    time.sleep(1)
    
    day_button = WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Data de Vencimento']")))

    day_button.click()

    metodo_pagamento_dropdown = driver.find_element(By.NAME, 'paymentMethod')
    select_m = Select(metodo_pagamento_dropdown)
    select_m.select_by_value('BOLETO')

    unidade_dropdown = driver.find_element(By.NAME, 'company')
    select_u = Select(unidade_dropdown)
    select_u.select_by_value(str(row['Unidade']))

    status_dropdown = driver.find_element(By.NAME, 'status')
    select_s = Select(status_dropdown)
    select_s.select_by_value('PENDING')

    id_boleto = row['Unidade']

    caminho_arquivo = r'Caminho\{}.pdf'.format(id_boleto)

    upload_boleto_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")

    upload_boleto_input.send_keys(caminho_arquivo)

    submit_button = driver.find_element(By.XPATH, "//button[@data-tour-id='page_button']")  #XPath do botão de envio
    submit_button.click()

    time.sleep(2)