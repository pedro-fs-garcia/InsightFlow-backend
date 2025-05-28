from functools import cache
from typing import List, Literal
import pandas as pd

from app.estatisticas.stats_utils import filtrar_df
from data_pipeline.models.vidente import Vidente

path = 'data_pipeline/datasets/dados_agregados/mv_sh4_mensal.csv'

# 'CO_SH4,CO_PAIS,SG_UF_NCM,VL_FOB_EXP,KG_LIQUIDO_EXP,VL_FOB_IMP,KG_LIQUIDO_IMP,DATA'

def hist_sh4 (df:pd.DataFrame, tipo:str, crit=Literal['KG_LIQUIDO', 'VL_FOB', 'balanca', 'valor_agregado']):
    coluna_crit = f"{crit}_{tipo}" if crit != 'balanca' else crit
    df = df.groupby('DATA')[[coluna_crit]].sum().reset_index()
    df_prophet = df.rename(columns={'DATA': 'ds', coluna_crit: 'y'})
    df_prophet['y'] = df_prophet['y'].fillna(0)
    return df_prophet

@cache
def tendencia_sh4(sh4: str, estado: str = None, pais: int = None):
    """
    Gera tendências de dados comerciais para um determinado código SH4,
    por estado e/ou país, usando previsões com o Prophet.
    
    Retorna um dicionário com as séries temporais previstas.
    """
    path = 'data_pipeline/datasets/dados_agregados/mv_sh4_mensal.csv'

    tendencia_dashboard = {}
    vidente = Vidente()  # Supondo que essa classe implemente .gerar_profecia_json()
    print("Argumentos recebidos:")
    print("sh4:", sh4)
    print("estado:", estado)
    print("pais:", pais)
    # Carregar e preparar os dados
    df = pd.read_csv(path, dtype={'CO_SH4': str})
    df['CO_SH4'] = df['CO_SH4'].astype(str)
    print("df antes da filtragem: ", df)
    # Filtragem por sh4, estado e país
    df = filtrar_df(df=df, sh4=sh4, pais=pais, estado=estado)

    # Verificações para evitar divisão por zero
    df['balanca'] = df['VL_FOB_EXP'] - df['VL_FOB_IMP']
    df['valor_agregado_EXP'] = df['VL_FOB_EXP'] / df['KG_LIQUIDO_EXP'].replace(0, pd.NA)
    df['valor_agregado_IMP'] = df['VL_FOB_IMP'] / df['KG_LIQUIDO_IMP'].replace(0, pd.NA)
    print("df após a filtragem: ", df)
    # Geração de tendências
    for crit in ['KG_LIQUIDO', 'VL_FOB', 'balanca', 'valor_agregado']:
        if crit != 'balanca':
            for tipo in ['EXP', 'IMP']:
                nome = f"{crit.lower()}_{tipo.lower()}"
                try:
                    df_temp = hist_sh4(df, tipo, crit)
                    tendencia = vidente.gerar_profecia_json(df_temp)
                    tendencia_dashboard[nome] = tendencia
                except Exception as e:
                    print(f"[ERRO] Falha ao gerar tendência para {nome}: {e}")
        else:
            nome = crit.lower()
            try:
                df_temp = hist_sh4(df, None, crit)
                tendencia = vidente.gerar_profecia_json(df_temp)
                tendencia_dashboard[nome] = tendencia
            except Exception as e:
                print(f"[ERRO] Falha ao gerar tendência para {nome}: {e}")
    print(tendencia_dashboard.keys())

    return tendencia_dashboard


# def tendencia_sh4(tipo: Literal['EXP', 'IMP'], sh4: str) -> List[dict]:
#     # app_logger.info(f"Iniciando análise de tendência de VL_FOB por SH4 {sh4} usando mv_sh4_mensal")

#     caminho_csv = "data_pipeline/datasets/dados_agregados/mv_sh4_mensal.csv"
#     df = pd.read_csv(caminho_csv)
#     tipo=tipo.upper()
#     print(tipo, sh4)
#     df['CO_SH4'] = df['CO_SH4'].astype(str)
#     df = df[df['CO_SH4'] == str(sh4)]

#     coluna_valor = f"VL_FOB_{tipo}"
#     df = df.groupby('DATA')[[coluna_valor]].sum().reset_index()
#     df_prophet = df.rename(columns={'DATA': 'ds', coluna_valor: 'y'})
#     df_prophet['y'] = df_prophet['y'].fillna(0)
#     print(df_prophet)
#     nome = f"tendencia_vlfob_{tipo.lower()}_sh4{sh4}"
#     vidente=Vidente()
#     return vidente.gerar_profecia(df_prophet, nome, f"Previsão de Valor FOB ({tipo}) - SH4 {sh4}", f"Valor FOB {tipo} ($)")
