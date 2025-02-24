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
from google.cloud import bigquery
import pandas as pd
import os
import pyperclip
import time
from selenium.webdriver.common.keys import Keys


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Credential local"

client = bigquery.Client()

ID_CNPJ = """
SELECT
    CONCAT(
        SUBSTRING(c.cnpj, 1, 2), '.', 
        SUBSTRING(c.cnpj, 3, 3), '.', 
        SUBSTRING(c.cnpj, 6, 3), '/', 
        SUBSTRING(c.cnpj, 9, 4), '-', 
        SUBSTRING(c.cnpj, 13, 2)
    ) AS cnpj,
    c.id
FROM `mais1cafe.company` as c
"""

query_job = client.query(ID_CNPJ)

results = query_job.result()

df_cnpj = pd.DataFrame([dict(row) for row in results])

planilha = pd.read_excel('Excel local')

planilha_merged = planilha.merge(df_cnpj[['id', 'cnpj']], left_on='Unidade', right_on='id', how='left')

if 'CNPJ' in planilha_merged.columns:
    planilha_merged['CNPJ'] = planilha_merged['cnpj']

planilha_merged = planilha_merged.drop(columns=['id', 'cnpj'])

planilha_merged.to_excel('Excel local', index=False)

print("Planilha atualizada com a coluna 'CNPJ'!")

driver = ('Drive local')

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

service = Service(driver)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://login.contaazul.com/#/')

time.sleep(3)

usuario_input = driver.find_element(By.XPATH, "//input[@type='email']")
usuario_input.send_keys('Email')

senha_input = driver.find_element(By.XPATH, "//input[@type='password']")
senha_input.send_keys('Password')

senha_input.send_keys(Keys.RETURN)

time.sleep(15)

driver.get('https://pro.contaazul.com/#/ca/vendas/vendas-e-orcamentos')

time.sleep(5)

WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@data-original-title='Anterior']"))
).click()

WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(((By.XPATH, "//*[@data-v-13d60518 and contains(text(), 'Mais filtros')]")))).click()

driver.find_element(By.XPATH, "//span[@data-original-title = 'Clique aqui para editar o filtro']").click()

WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//div[@value = 'ds-option--select-all']"))
).click()

WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "(//div[@value = '[object Object]'])[3]"))
).click()

WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(((By.XPATH, "//button[@class = 'ds-multiple-select-filter__apply-button ds-button ds-button-secondary ds-button-md ds-u-width--full'  and contains(text(), 'Aplicar')]")))).click()

time.sleep(2)

WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(((By.XPATH, "//*[@data-v-13d60518 and contains(text(), 'Mais filtros')]")))).click()

time.sleep(2)

driver.find_element(By.XPATH, "//*[@data-v-85c9500b and contains(text(), 'Cliente')]").click()

time.sleep(2)

input_field = driver.find_element(By.XPATH, "//div[@class='ds-input__container']/input[not(@placeholder)]")

planilha = pd.read_excel('Excel Local')

primeira_execucao = True

for cnpj in planilha['CNPJ']:
    
    if primeira_execucao:
        
        input_field.send_keys(str(cnpj))

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//div[@value = '[object Object]'])[1]"))
        )

        time.sleep(2)
        
        driver.find_element(By.XPATH, "(//div[@value = '[object Object]'])[1]").click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class = 'ds-multiple-select-filter__apply-button ds-button ds-button-secondary ds-button-md ds-u-width--full'  and contains(text(), 'Aplicar')]"))
        ).click()

        time.sleep(2)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@data-v-13d60518 and contains(text(), 'Ações')]"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@data-v-85c9500b and contains(text(), 'Editar')]"))
        ).click()

        time.sleep(5)

        driver.find_element(By.XPATH, "(//label[@class='ds-radio__label'])[1]").click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ds-button-primary') and contains(text(), 'Confirmar')]"))
        ).click()

        time.sleep(3)

        valor_input = driver.find_element(By.XPATH, "//input[@data-appcues='sale-edit-item-value']")

        valor = planilha.loc[planilha['CNPJ'] == cnpj, 'Valor'].values[0]
        valor_formatado = str(valor).replace('.', ',')

        pyperclip.copy(valor_formatado)

        valor_input.click()

        valor_input.send_keys(Keys.CONTROL, 'v')

        time.sleep(1)

        desconto_input = driver.find_element(By.XPATH, "//div[@class='ds-input--with-addon ds-currency-input' and @data-v-440d3c3c]//input[@type='text' and @class='ds-input ds-form-control']")
        desconto = planilha.loc[planilha['CNPJ'] == cnpj, 'Desconto'].values[0]
        desconto_formatado = str(desconto).replace('.', ',')

        pyperclip.copy(desconto_formatado)

        driver.execute_script("arguments[0].click();", desconto_input)

        desconto_input.send_keys(Keys.CONTROL, 'v')

        driver.find_element(By.TAG_NAME, "html").click()

        time.sleep(2)

        button = driver.find_element(By.XPATH, "//div[@class='ds-footer ds-rollover-footer' and @data-v-8c16e35d]//div[@class='ds-footer__content ds-u-display--flex ds-u-justify-content--space-between']//button[@class='ds-loader-button__button ds-button ds-button-primary ds-button-md']")
        driver.execute_script("arguments[0].click();", button)

        time.sleep(3)

        primeira_execucao = False

    else:

        driver.find_element(By.XPATH, "//span[@data-v-8d94db41 and contains(text(), 'Cliente:')]").click()

        time.sleep(2)
        
        driver.find_element(By.XPATH, "//input[@data-v-3689d29a and contains(@class, 'ds-input') and contains(@class, 'ds-form-control') and not(@placeholder)]").send_keys(str(cnpj))  # Insere o CNPJ no campo de pesquisa

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//div[@value = '[object Object]'])[1]"))
        )

        time.sleep(2)
        
        driver.find_element(By.XPATH, "(//div[@value = '[object Object]'])[1]").click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class = 'ds-multiple-select-filter__apply-button ds-button ds-button-secondary ds-button-md ds-u-width--full'  and contains(text(), 'Aplicar')]"))
        ).click()

        time.sleep(2)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@data-v-13d60518 and contains(text(), 'Ações')]"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@data-v-85c9500b and contains(text(), 'Editar')]"))
        ).click()

        time.sleep(5)

        driver.find_element(By.XPATH, "(//label[@class='ds-radio__label'])[1]").click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ds-button-primary') and contains(text(), 'Confirmar')]"))
        ).click()

        time.sleep(3)

        valor_input = driver.find_element(By.XPATH, "//input[@data-appcues='sale-edit-item-value']")

        valor = planilha.loc[planilha['CNPJ'] == cnpj, 'Valor'].values[0]
        valor_formatado = str(valor).replace('.', ',')

        pyperclip.copy(valor_formatado)

        valor_input.click()

        valor_input.send_keys(Keys.CONTROL, 'v')

        time.sleep(1)

        desconto_input = driver.find_element(By.XPATH, "//div[@class='ds-input--with-addon ds-currency-input' and @data-v-440d3c3c]//input[@type='text' and @class='ds-input ds-form-control']")
        desconto = planilha.loc[planilha['CNPJ'] == cnpj, 'Desconto'].values[0]
        desconto_formatado = str(desconto).replace('.', ',')
        
        pyperclip.copy(desconto_formatado)

        driver.execute_script("arguments[0].click();", desconto_input)

        desconto_input.send_keys(Keys.CONTROL, 'v')

        driver.find_element(By.TAG_NAME, "html").click()

        time.sleep(2)

        button = driver.find_element(By.XPATH, "//div[@class='ds-footer ds-rollover-footer' and @data-v-8c16e35d]//div[@class='ds-footer__content ds-u-display--flex ds-u-justify-content--space-between']//button[@class='ds-loader-button__button ds-button ds-button-primary ds-button-md']")
        driver.execute_script("arguments[0].click();", button)

        time.sleep(3)




