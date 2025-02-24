from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pyperclip
import time
import random
import pandas as pd

# Caminho para o ChromeDriver
driver_p = ('Driver Local')

# Caminho para o arquivo Excel
excel_path = ('Excel local')

df = pd.read_excel(excel_path)

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

service = Service(driver_p)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://web.whatsapp.com/")

print("Escaneie o código QR do WhatsApp Web!")
time.sleep(35)

driver.minimize_window()

mensagens = [
    """Message 1""",
    
    """Message 2""",
    
    """Message 3"""
]

tempos_espera = [17, 28, 37, 60, 83, 94, 112]

def enviar_mensagens_aleatorias():
    for _, row in df.iterrows():
        contato = row["Cell"]
        #unidade = row["Unit"]  # When we have the Unit Name on the message
        
        mensagem_escolhida = random.choice(mensagens)
        
        # Substitui o marcador {unit} pela unidade específica
        #mensagem_escolhida = mensagem_escolhida.format(unit=unidade)

        tempo_espera = random.choice(tempos_espera)

        driver.execute_script(f"window.open('https://web.whatsapp.com/send?phone={contato}', '_blank');")

        driver.switch_to.window(driver.window_handles[-1])

        time.sleep(25)
        
        message_box = driver.find_element(By.XPATH, "//div[@aria-placeholder = 'Digite uma mensagem']")
        
        pyperclip.copy(mensagem_escolhida)

        message_box.click()

        message_box.send_keys(Keys.CONTROL, 'v')

        time.sleep(1)
        
        message_box.send_keys(Keys.RETURN)

        time.sleep(tempo_espera)

        driver.close()

        driver.switch_to.window(driver.window_handles[0])

        print(f"Mensagem enviada para {contato}: '{mensagem_escolhida}'")
        print(f"Aguardando {tempo_espera} segundos antes de enviar para o próximo contato...\n")

enviar_mensagens_aleatorias()
driver.quit()
