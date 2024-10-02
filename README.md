### Base de dados
Vendas da amazon 
- Colunas:
  - Category: Tipo de produto. (String)
  - Size: Tamanho do produto. (String)
  - Date: Data da venda. (Data)
  - Status: Status da venda. (String)
  - Fulfilment: Método de entrega. (String)
  - Style: Estilo do produto. (String)
  - SKU: Unidade de Manutenção de Estoque. (String)
  - ASIN: Número de Identificação Padrão da Amazon. (String)
  - Courier Status: Status do serviço de entrega. (String)
  - Qty: Quantidade do produto. (Inteiro)
  - Amount: Valor da venda. (Float)
  - B2B: Venda de empresa para empresa. (Booleano)
  - Currency: A moeda utilizada na venda. (String)







### Tratamento de dados


  ```py
  # 1. Substituir valores NaN na coluna 'Courier Status' por 'unknown'
  df['Courier Status'].fillna('unknown', inplace=True)
  
  # 2. Substituir valores NaN na coluna 'currency' por 'unknown'
  df['currency'].fillna('unknown', inplace=True)
  
  # 3. Substituir valores NaN na coluna 'Amount' pela média da categoria
  # Supondo que a coluna 'categoria' é a coluna pela qual será calculada a média
  df['Amount'] = df.groupby('Category')['Amount'].transform(lambda x: x.fillna(x.mean()))
  
  # 4. Transformar '#promotion_id' em True (quando houver ID) e False (quando não houver ID)
  df['promotion-ids'] = df['promotion-ids'].notna()
  
  # 5. Dropar as colunas 'fufilled by' e 'unnamed'
  df.drop(columns=['fulfilled-by', 'Unnamed: 22','SKU'], inplace=True)

  # 6. Mudar tipo de 'object' para datetime
  df['Date']=pd.to_datetime(df['Date']

  #7. Renomear coluna para facilitar na hora da análise
  df.rename(columns={'Sales Channel ': 'Sales Channel'},inplace=True)

```
