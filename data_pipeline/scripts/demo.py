import pandas as pd
import matplotlib.pyplot as plt

# Carregar os arquivos CSV
exp_path = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2024.csv"
uf_path = "https://balanca.economia.gov.br/balanca/bd/tabelas/UF.csv"
ncm_path = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM.csv"
pais_path = "https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv"

# Ler os dados
exp_df = pd.read_csv(exp_path, sep=";", encoding="latin1")
uf_df = pd.read_csv(uf_path, sep=";", encoding="latin1")
ncm_df = pd.read_csv(ncm_path, sep=";", encoding="latin1")
pais_df = pd.read_csv(pais_path, sep=";", encoding="latin1")

# Merge com a descrição dos produtos
exp_df = exp_df.merge(ncm_df[['CO_NCM', 'NO_NCM_POR']], on='CO_NCM', how='left')

# Remover estados com sigla 'ND' e criar uma cópia para evitar warnings
exp_df = exp_df[exp_df['SG_UF_NCM'] != 'ND'].copy()

# Calcular valor agregado (VL_FOB por KG_LIQUIDO)
exp_df.loc[:, 'VALOR_AGREGADO'] = exp_df['VL_FOB'] / exp_df['KG_LIQUIDO']

# Remover valores infinitos ou NaN
exp_df = exp_df.dropna(subset=['VALOR_AGREGADO'])
exp_df = exp_df[exp_df['VALOR_AGREGADO'] != float('inf')]

# Agrupar por estado e produto, somando peso e valor FOB
ranking = exp_df.groupby(['SG_UF_NCM', 'NO_NCM_POR'])[['KG_LIQUIDO', 'VL_FOB']].sum().reset_index()

# Calcular o valor agregado médio por estado
ranking['VALOR_AGREGADO'] = ranking['VL_FOB'] / ranking['KG_LIQUIDO']

# Ordenar pelo maior valor agregado
ranking_sorted = ranking.sort_values(by='VALOR_AGREGADO', ascending=False)

# Exibir os top 10 produtos com maior valor agregado
print("Top 10 produtos com maior valor agregado:")
print(ranking_sorted.head(10))

# Cálculo da média e mediana por estado
estado_valor_agregado = ranking.groupby('SG_UF_NCM')['VALOR_AGREGADO'].mean().sort_values(ascending=False)
estado_valor_agregado_mediana = ranking.groupby('SG_UF_NCM')['VALOR_AGREGADO'].median().sort_values(ascending=False)

# Identificar o país que teve o maior valor agregado total por estado
pais_destino = exp_df.groupby(['SG_UF_NCM', 'CO_PAIS'])[['VL_FOB', 'KG_LIQUIDO']].sum().reset_index()
pais_destino['VALOR_AGREGADO'] = pais_destino['VL_FOB'] / pais_destino['KG_LIQUIDO']

# Obter o país com maior valor agregado total por estado
pais_top = pais_destino.loc[pais_destino.groupby('SG_UF_NCM')['VALOR_AGREGADO'].idxmax()]

# Fazer merge para obter o nome do país
pais_top = pais_top.merge(pais_df[['CO_PAIS', 'NO_PAIS']], on='CO_PAIS', how='left')

# Exibir o principal país de destino por estado baseado no valor agregado total
print("Principal país de destino por estado (maior valor agregado total):")
print(pais_top[['SG_UF_NCM', 'NO_PAIS', 'VALOR_AGREGADO']])

# Plotar a média do valor agregado
plt.figure(figsize=(12, 6))
estado_valor_agregado.head(10).plot(kind='bar', color='blue')
plt.title('Top 10 Estados com Maior Valor Agregado Médio de Exportação')
plt.xlabel('Estado')
plt.ylabel('Valor Agregado Médio (VL_FOB / KG_LIQUIDO)')
plt.xticks(rotation=45)
plt.show()

# Plotar a mediana do valor agregado
plt.figure(figsize=(12, 6))
estado_valor_agregado_mediana.head(10).plot(kind='bar', color='green')
plt.title('Top 10 Estados com Maior Valor Agregado Mediano de Exportação')
plt.xlabel('Estado')
plt.ylabel('Valor Agregado Mediano (VL_FOB / KG_LIQUIDO)')
plt.xticks(rotation=45)
plt.show()