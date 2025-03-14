# Limpeza e Filtragem de Dados do Comex Stat (2014-2024)

# Remover registros com peso 0
#remover registros com estado ND
# remover valores infinitos nan e divisões por zero
# remover vias de transporte inválidas
# remover rotas absurdas (ex: brasil -> Arábia Saudita via rodoviária)

import pandas as pd

from models.tabelasComexStat import TabelasComexStat


tabelas_cs = TabelasComexStat()
dataframe = pd.read_csv(tabelas_cs.exportacao_ncm('2014'), delimiter=';', encoding='latin1')



# Carregar dados brutos (exemplo CSV local)
df = pd.read_csv('https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2024.csv', delimiter=';', encoding='latin1')

# Análise inicial dos dados
print("Resumo dos dados:")
print(df.info())
print("\nEstatísticas descritivas:")
print(df.describe())
print("\nColuinas")
print(df.columns)

# Remover registros com peso líquido = 0
df = df[df['KG_LIQUIDO'] > 0]

# Remover estados com sigla 'ND' e criar uma cópia para evitar warnings
df = df[df['SG_UF_NCM'] != 'ND'].copy()

# Calcular valor agregado (VL_FOB por KG_LIQUIDO)
df.loc[:, 'VALOR_AGREGADO'] = df['VL_FOB'] / df['KG_LIQUIDO']

# Criar coluna de Valor Agregado (VA)
# df['VA'] = df['VL_FOB'] / df['KG_LIQUIDO']

# Remover valores infinitos ou NaN
df = df.dropna(subset=['VALOR_AGREGADO'])
df = df[df['VALOR_AGREGADO'] != float('inf')]

# Filtrar vias de transporte inválidas
vias_validas = ['Marítima', 'Aérea', 'Rodoviária', 'Ferroviária']
df = df[df['CO_VIA'].isin(vias_validas)]

# Remover rotas absurdas (exemplo: Brasil -> Arábia Saudita via rodoviária)
rotas_invalidas = (df['CO_PAIS'] == 'ARÁBIA SAUDITA') & (df['CO_VIA'] == 'Rodoviária')
df = df[~rotas_invalidas]

# Salvar o dataset limpo
output_path = 'data_pipeline/datasets/limpo/comex_stat_limpo.csv'
df.to_csv(output_path, index=False, encoding='latin1')

print(f"Dados limpos salvos em: {output_path}")