import os
import time
import pandas as pd

def rename_file_with_retry(old_path, new_path, max_retries=5, wait_time=1):
    """
    Tenta renomear o arquivo com tentativas de reprocessamento se estiver em uso.
    
    :param old_path: Caminho do arquivo atual.
    :param new_path: Novo caminho para o arquivo.
    :param max_retries: Número máximo de tentativas de renomeação.
    :param wait_time: Tempo de espera entre as tentativas (em segundos).
    :return: Booleano indicando se o arquivo foi renomeado com sucesso.
    """
    retries = 0
    while retries < max_retries:
        try:
            os.rename(old_path, new_path)
            print(f"Arquivo renomeado com sucesso: {old_path} -> {new_path}")
            return True
        except OSError as e:
            if e.errno == 32:
                print(f"Erro: Arquivo em uso - Tentando novamente em {wait_time} segundos...")
                time.sleep(wait_time)
                retries += 1
            else:
                print(f"Erro ao tentar renomear o arquivo: {e}")
                return False
    print(f"Falha ao renomear o arquivo após {max_retries} tentativas.")
    return False

def rename_files_in_directory(directory, excel_file, max_retries=5, wait_time=1):
    """
    Percorre todos os arquivos no diretório e tenta renomeá-los com base nos IDs da planilha Excel.
    
    :param directory: Diretório onde os arquivos estão localizados.
    :param excel_file: Caminho do arquivo Excel que contém os IDs da unidade.
    :param max_retries: Número máximo de tentativas de renomeação.
    :param wait_time: Tempo de espera entre as tentativas (em segundos).
    """
    df = pd.read_excel(excel_file)
    
    for i, row in df.iterrows():
        unidade_id = row['ID Unidade']
        old_filename = row['Nome do Boleto']
        old_file_path = os.path.join(directory, old_filename)
        new_filename = f"{unidade_id}.pdf"
        new_file_path = os.path.join(directory, new_filename)
        
        print(f"Tentando renomear o arquivo {old_filename} ({i+1}/{len(df)})...")
        
        rename_file_with_retry(old_file_path, new_file_path, max_retries, wait_time)

directory = "Local"

excel_file = "Local"

rename_files_in_directory(directory, excel_file)
