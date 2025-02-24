from google.cloud import bigquery
import pandas as pd
import requests
import re
import pdfplumber
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/Administrativo/Documents/@GOOGLE CREDENTIALS/business-intelligence-423313-cbfb3b76e9dd.json"

client = bigquery.Client()

sql_query = """
WITH cnpj AS (
    SELECT
        c.id,
        CONCAT(
            SUBSTRING(c.cnpj, 1, 2), '.', 
            SUBSTRING(c.cnpj, 3, 3), '.', 
            SUBSTRING(c.cnpj, 6, 3), '/', 
            SUBSTRING(c.cnpj, 9, 4), '-', 
            SUBSTRING(c.cnpj, 13, 2)
        ) AS cnpj
    FROM `mais1cafe.company` AS c
)
SELECT
  b.id,
  cnpj.cnpj,
  FORMAT_DATE('%d/%m/%Y', CAST(b.due_date AS DATE)) as due_date,
  REPLACE(FORMAT('%.2f', CASE
    WHEN b.net_value > 0 THEN b.net_value
    WHEN b.net_value = 0 OR b.net_value IS NULL THEN b.value
  END), '.', ',') AS value,
  b.billet
FROM `mais1cafe.bill` AS b
LEFT JOIN cnpj ON b.company_id = cnpj.id
WHERE 
  b.billet IS NOT NULL AND
  b.provider_id = 209
  AND
  EXTRACT(YEAR from b.due_date) >= 2025
"""

output_file = 'Create Sheet'

query_job = client.query(sql_query)

results = query_job.result()

df_bigquery = pd.DataFrame([dict(row) for row in results])

def extract_pdf_data(pdf_url):
    try:
        response = requests.get(pdf_url, timeout=30)
        pdf_file = response.content

        with open("temp_boleto.pdf", "wb") as f:
            f.write(pdf_file)

        with pdfplumber.open("temp_boleto.pdf") as pdf:
            page = pdf.pages[0]
            text = page.extract_text()

        os.remove("temp_boleto.pdf")

        cnpj = re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', text)
        due_date = re.search(r"Vencimento[:\s]*([\d]{2}/[\d]{2}/[\d]{4})", text)
        value = re.search(r"Valor\s*Cobrado[\s]*([\d]{1,3}(\.\d{3})*,\d{2})", text)

        return (
            cnpj.group(0) if cnpj else None,
            due_date.group(1) if due_date else None,
            value.group(1) if value else None
        )

    except Exception as e:
        print(f"Erro ao extrair dados do boleto: {e}")
        return None, None, None

def clean_value(value):
    """Função para limpar e normalizar os valores para comparação."""
    if value:
        value = value.replace('.', '').replace(' ', '').strip()
        return value
    return None

def clean_date(date):
    """Função para normalizar datas no formato dd/mm/aaaa."""
    if date:
        return date.strip()
    return None

comparison_results = []
for index, row in df_bigquery.iterrows():
    cnpj_sql = row['cnpj']
    due_date_sql = clean_date(str(row['due_date']))
    value_sql = clean_value(str(row['value']))
    billet_url = row['billet']

    cnpj_pdf, due_date_pdf, value_pdf = extract_pdf_data(billet_url)

    value_pdf = clean_value(value_pdf)
    due_date_pdf = clean_date(due_date_pdf)

    cnpj_ok = 'ok' if cnpj_sql and cnpj_pdf and cnpj_sql == cnpj_pdf else 'não'
    due_date_ok = 'ok' if due_date_sql and due_date_pdf and due_date_sql == due_date_pdf else 'não'
    value_ok = 'ok' if value_sql and value_pdf and value_sql == value_pdf else 'não'

    comparison_results.append({
        'id': row['id'],
        'cnpj_sql': cnpj_sql,
        'cnpj_pdf': cnpj_pdf,
        'cnpj_ok': cnpj_ok,
        'due_date_sql': due_date_sql,
        'due_date_pdf': due_date_pdf,
        'due_date_ok': due_date_ok,
        'value_sql': value_sql,
        'value_pdf': value_pdf,
        'value_ok': value_ok,
        'billet': billet_url
    })

    if (index + 1) % 100 == 0:
        print(f"{index + 1} boletos analisados...")

df_comparison = pd.DataFrame(comparison_results)

'''# Filtrar apenas os boletos que não batem
df_filtered = df_comparison[(df_comparison['cnpj_ok'] == 'não') | 
                            (df_comparison['due_date_ok'] == 'não') | 
                            (df_comparison['value_ok'] == 'não')]
'''
# Salvar o resultado final em uma nova planilha
#I deleted from this script the dort option just for this case
df_comparison.to_excel(output_file, index=False)

print("Comparação concluída e planilha salva com os boletos não correspondentes.")