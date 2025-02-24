import os
import json
import shutil
from google.cloud import bigquery
from datetime import datetime, date
from decimal import Decimal


# Configuração para autenticação no BigQuery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Credentials"

# Configurações do BigQuery
client = bigquery.Client()

# Consulta para atualizar o dataset da mais 1 no BigQuery
update_mais1_dataset_query = """
CREATE OR REPLACE TABLE `business-intelligence-423313.bi_query_tables.mais_1_billing` AS
    WITH Ultima_venda AS (
        SELECT
            s.company_id,
            MAX(s.date) AS ultima_data
        FROM `business-intelligence-423313.mais1cafe.sale` AS s
        GROUP BY company_id
    )
    SELECT
        b.id AS ID,
        b.`date` AS _date,
        b.due_date AS Due_date,
        b.payday AS Pay_date,
        COALESCE(b.description, '') AS Description,
        b.value AS Value,
        b.net_value AS Net_value,
        b.status AS Status,
        b.observation AS Observation,
        b.company_id AS Company_ID,
        c.name AS Name,
        c.cnpj AS CNPJ,
        mb.Sigla AS MB,
        CASE
            WHEN uv.ultima_data < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY) THEN "Fechada"
            ELSE "Aberta"
        END AS situacao_unidade,
        ccb.consultant_name,
        b.payment_method AS Method
    FROM `business-intelligence-423313.mais1cafe.bill` AS b
    LEFT JOIN `business-intelligence-423313.mais1cafe.company` AS c ON c.id = b.company_id
    LEFT JOIN `business-intelligence-423313.views_bi.company_consultant_BI` AS ccb ON b.company_id = ccb.company_id
    LEFT JOIN Ultima_venda AS uv ON b.company_id = uv.company_id
    LEFT JOIN `business-intelligence-423313.Martin_brower.MB` AS mb ON mb.CNPJ = c.cnpj
    WHERE provider_id = 932;
"""

# Consulta para atualizar o dataset da Pro no BigQuery
update_pro_dataset_query = """
CREATE OR REPLACE TABLE `business-intelligence-423313.bi_query_tables.Pro_billing` as
    WITH Ultima_venda AS (
    SELECT
        s.company_id,
        MAX(s.date) AS ultima_data
    FROM `business-intelligence-423313.mais1cafe.sale` AS s
    GROUP BY 
        company_id
)

SELECT
    b.id AS ID,
    b.`date` AS _date,
    b.due_date AS Due_date,
    b.payday AS Pay_date,
    -- Usando COALESCE para garantir que sempre tenha valor
    COALESCE(b.description, '') AS Description,
    b.value AS Value,
    b.net_value AS Net_value,
    b.status AS Status,
    b.observation AS Observation,
    b.company_id AS Company_ID,
    c.name AS Name,
    c.cnpj AS CNPJ,
    mb.Sigla AS MB,
    CASE
        WHEN uv.ultima_data < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY) THEN "Fechada"
        ELSE "Aberta"
    END AS situacao_unidade,
    ccb.consultant_name,
    b.payment_method AS Method
FROM `business-intelligence-423313.mais1cafe.bill` AS b
LEFT JOIN `business-intelligence-423313.mais1cafe.company` AS c ON c.id = b.company_id
LEFT JOIN `business-intelligence-423313.views_bi.company_consultant_BI` AS ccb ON b.company_id = ccb.company_id
LEFT JOIN Ultima_venda AS uv ON b.company_id = uv.company_id
LEFT JOIN `business-intelligence-423313.Martin_brower.MB` AS mb ON mb.CNPJ = c.cnpj
WHERE provider_id = 209;
"""

# Consulta para atualizar o dataset no BigQuery
update_dataset_query = """
CREATE OR REPLACE TABLE `business-intelligence-423313.bi_query_tables.billing` AS
WITH Ultima_venda AS (
    SELECT
        s.company_id,
        MAX(s.date) AS ultima_data
    FROM `business-intelligence-423313.mais1cafe.sale` AS s
    GROUP BY 
        s.company_id
),
Qtd_titulos_209 AS (
    SELECT 
        b.company_id,
        COUNT(*) AS quantidade_titulos_209
    FROM `business-intelligence-423313.mais1cafe.bill` AS b
    WHERE b.provider_id = 209 AND
    (b.Status = 0 OR b.Status = 2)
    GROUP BY b.company_id
),
Qtd_titulos_932 AS (
    SELECT 
        b.company_id,
        COUNT(*) AS quantidade_titulos_932
    FROM `business-intelligence-423313.mais1cafe.bill` AS b
    WHERE b.provider_id = 932 AND
    (b.Status = 0 OR b.Status = 2)
    GROUP BY b.company_id
)

SELECT
    b.id AS ID,
    b.`date` AS _date,
    b.due_date AS Due_date,
    b.payday AS Pay_date,
    COALESCE(b.description, '') AS Description,
    b.value AS Value,
    b.net_value AS Net_value,
    b.status AS Status,
    b.observation AS Observation,
    b.company_id AS Company_ID,
    c.name AS Name,
    c.cnpj AS CNPJ,
    b.provider_id AS Fornecedor,
    mb.Sigla AS MB,
    CASE
        WHEN uv.ultima_data < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY) THEN "Fechada"
        ELSE "Aberta"
    END AS situacao_unidade,
    ccb.consultant_name,
    b.payment_method AS Method,
    COALESCE(qt209.quantidade_titulos_209, 0) AS Qtd_Titulos_209,
    COALESCE(qt932.quantidade_titulos_932, 0) AS Qtd_Titulos_932
FROM `business-intelligence-423313.mais1cafe.bill` AS b
LEFT JOIN `business-intelligence-423313.mais1cafe.company` AS c ON c.id = b.company_id
LEFT JOIN `business-intelligence-423313.views_bi.company_consultant_BI` AS ccb ON b.company_id = ccb.company_id
LEFT JOIN Ultima_venda AS uv ON b.company_id = uv.company_id
LEFT JOIN `business-intelligence-423313.Martin_brower.MB` AS mb ON mb.CNPJ = c.cnpj
LEFT JOIN Qtd_titulos_209 AS qt209 ON qt209.company_id = b.company_id
LEFT JOIN Qtd_titulos_932 AS qt932 ON qt932.company_id = b.company_id
WHERE (b.provider_id = 209 OR b.provider_id = 932)
  AND (b.Status = 0 OR b.Status = 2);
"""

# Consulta principal para obter os dados atualizados
query_mais1 = """
SELECT * FROM `business-intelligence-423313.bi_query_tables.mais_1_billing`
"""
query_pro = """
SELECT * FROM `business-intelligence-423313.bi_query_tables.Pro_billing`
"""
query_ = """
SELECT * FROM `business-intelligence-423313.bi_query_tables.billing`
"""

# Caminhos para o arquivo JSON
json_file_mais1_path_onedrive = 'Local'
json_file_pro_path_onedrive = 'Local'
json_file_path_onedrive = 'Local'

temporary_mais1_json_path = 'Local'
temporary_pro_json_path = 'Local'
temporary_json_path = 'Local'

def update_mais1_dataset():
    """Executa a consulta para atualizar o dataset no BigQuery."""
    print("Atualizando mais1_dataset no BigQuery...")
    job = client.query(update_mais1_dataset_query)
    job.result()
    print("Dataset atualizado com sucesso.")

def update_pro_dataset():
    """Executa a consulta para atualizar o dataset no BigQuery."""
    print("Atualizando pro_dataset no BigQuery...")
    job = client.query(update_pro_dataset_query)
    job.result()
    print("Dataset atualizado com sucesso.")

def update_dataset():
    """Executa a consulta para atualizar o dataset no BigQuery."""
    print("Atualizando pro_dataset no BigQuery...")
    job = client.query(update_dataset_query)
    job.result()
    print("Dataset atualizado com sucesso.")

def run_query_and_save_mais1_json():
    """Executa a consulta principal e salva os resultados como JSON."""
    temp_dir = os.path.dirname(temporary_mais1_json_path)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    job = client.query(query_mais1)
    results = job.result()
    
    data = [dict(row) for row in results]

    def custom_converter(o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, Decimal):
            return float(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    with open(temporary_mais1_json_path, "w") as json_file:
        json.dump(data, json_file, default=custom_converter)
    
    print("Consulta BigQuery salva como JSON mais 1 temporário.")

def run_query_and_save_pro_json():
    """Executa a consulta principal e salva os resultados como JSON."""
    temp_dir = os.path.dirname(temporary_pro_json_path)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    job = client.query(query_pro)
    results = job.result()
    
    data = [dict(row) for row in results]

    def custom_converter(o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, Decimal):
            return float(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    with open(temporary_pro_json_path, "w") as json_file:
        json.dump(data, json_file, default=custom_converter)
    
    print("Consulta BigQuery salva como JSON pro temporário.")

def run_query_and_save_json():
    """Executa a consulta principal e salva os resultados como JSON."""
    temp_dir = os.path.dirname(temporary_json_path)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    job = client.query(query_)
    results = job.result()
    
    data = [dict(row) for row in results]

    def custom_converter(o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, Decimal):
            return float(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    with open(temporary_json_path, "w") as json_file:
        json.dump(data, json_file, default=custom_converter)
    
    print("Consulta BigQuery salva como JSON pro temporário.")

def replace_mais1_json_in_onedrive():
    """Substitui o arquivo JSON existente no OneDrive pelo novo."""
    if os.path.exists(json_file_mais1_path_onedrive):
        os.remove(json_file_mais1_path_onedrive)
    shutil.move(temporary_mais1_json_path, json_file_mais1_path_onedrive)
    print("Arquivo JSON no OneDrive atualizado.")

def replace_pro_json_in_onedrive():
    """Substitui o arquivo JSON existente no OneDrive pelo novo."""
    if os.path.exists(json_file_pro_path_onedrive):
        os.remove(json_file_pro_path_onedrive)
    shutil.move(temporary_pro_json_path, json_file_pro_path_onedrive)
    print("Arquivo JSON no OneDrive atualizado.")

def replace_json_in_onedrive():
    """Substitui o arquivo JSON existente no OneDrive pelo novo."""
    if os.path.exists(json_file_path_onedrive):
        os.remove(json_file_path_onedrive)
    shutil.move(temporary_json_path, json_file_path_onedrive)
    print("Arquivo JSON no OneDrive atualizado.")
        

update_mais1_dataset()
update_pro_dataset()
update_dataset()
run_query_and_save_mais1_json()
run_query_and_save_pro_json()
run_query_and_save_json()
replace_mais1_json_in_onedrive()
replace_pro_json_in_onedrive()
replace_json_in_onedrive()

