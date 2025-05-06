import json
import os
from typing import List, Literal
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pandas.tseries.offsets import MonthEnd
import warnings

from data_pipeline.models.gera_dataframes import GeradorDeDataFrames
from app.utils.logging_config import app_logger, error_logger


warnings.filterwarnings("ignore")


class Vidente():
    def __init__(self):
        self.gd = GeradorDeDataFrames()
        self.output_dir = 'data_pipeline/datasets/tendencias'
        os.makedirs(self.output_dir, exist_ok=True)
        return
    

    def gerar_profecia(self, df_prophet: pd.DataFrame, nome_arquivo: str, titulo_graf: str, ylabel: str):
        if len(df_prophet) < 2:
            print("Dados insuficientes para modelagem.")
            return

        df = df_prophet.copy()
        df['ds'] = pd.to_datetime(df['ds'])
        df.set_index('ds', inplace=True)
        df = df.asfreq('MS')  #frequência mensal com início no início do mês
        df['y'] = df['y'].interpolate() 

        modelo = SARIMAX(df['y'], order=(1,1,1), seasonal_order=(1,1,1,12), enforce_stationarity=False, enforce_invertibility=False)
        modelo_fit = modelo.fit(disp=False)

        n_periods = 24
        future_index = pd.date_range(start=df.index[-1] + MonthEnd(1), periods=n_periods, freq='MS')
        previsoes = modelo_fit.forecast(steps=n_periods)

        df_previsao = pd.concat([df['y'], pd.Series(previsoes, index=future_index)], axis=0)
        
        plt.figure(figsize=(10, 5))
        df_previsao.plot(label='Previsão')
        plt.axvline(df.index[-1], color='gray', linestyle='--', label='Início da previsão')
        plt.title(titulo_graf)
        plt.xlabel('Data')
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/{nome_arquivo}.png', dpi=300)
        plt.close()

        resultado = df_previsao.reset_index()
        resultado.columns = ['ds', 'yhat']
        resultado['ds'] = resultado['ds'].astype(str)

        app_logger.info("Análise de tendências por NCM finalizada")
        return resultado.to_dict(orient='records')



    def tendencia_balanca_comercial(self, 
        estado: str|None = None,
        pais: int|None = None
    ) -> List[dict] | None:
        app_logger.info(f"Iniciando análise de tendência de Balança Comercial")        
        df = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_balanca_comercial.csv")

        if estado:
            df = df[df['SG_UF_NCM'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]

        df = df.groupby('DATA')[['balanca_comercial']].sum().reset_index()
        df_prophet = df[['DATA', 'balanca_comercial']].rename(columns={'DATA': 'ds', 'balanca_comercial': 'y'})

        nome = f"tendencia_balanca_comercial"
        if estado:
            nome += f"_e{estado}"
        if pais:
            nome += f"_p{pais}"
        return self.gerar_profecia(df_prophet, nome, f"Previsão de Balança Comercial", "Balança Comercial ($)")


    def tendencia_vlfob(self, 
        tipo: Literal['EXP', 'IMP'],
        estado: str|None = None,
        pais: int|None = None
    ) -> List[dict]:
        app_logger.info(f"Iniciando análise de tendência de Valor FOB de {tipo}")
        df = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_balanca_comercial.csv")

        if estado:
            df = df[df['SG_UF_NCM'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]

        df = df.groupby('DATA')[[f'VL_FOB_{tipo}']].sum().reset_index()
        df_prophet = df[['DATA', f'VL_FOB_{tipo}']].rename(columns={'DATA': 'ds', f'VL_FOB_{tipo}': 'y'})

        nome = f"tendencia_vlfob_{tipo.lower()}"
        if estado:
            nome += f"_e{estado}"
        if pais:
            nome += f"_p{pais}"
        return self.gerar_profecia(df_prophet, nome, f"Previsão de Valor Fob de {tipo}", f"Valor Fob {tipo} ($)")

    
    def tendencia_valor_agregado(self, tipo:Literal['EXP', 'IMP'], estado:str|None = None, pais:int|None = None) -> List[dict]:
        app_logger.info(f"Iniciando análise de tendência de Valor Agregado de {tipo}")
        df = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_balanca_comercial.csv")
        if tipo == 'EXP':
            df = df.drop(columns=['VL_FOB_IMP', 'KG_LIQUIDO_IMP'])
        elif tipo == 'IMP':
            df = df.drop(columns=['VL_FOB_EXP', 'KG_LIQUIDO_EXP'])

        if estado:
            df = df[df['SG_UF_NCM'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]

        df = df.groupby('DATA')[[f'VL_FOB_{tipo}', f'KG_LIQUIDO_{tipo}']].sum().reset_index()
        df['valor_agregado'] = df[f'VL_FOB_{tipo}'] / df[f'KG_LIQUIDO_{tipo}']
        df_prophet = df[['DATA', 'valor_agregado']].rename(columns={'DATA': 'ds', 'valor_agregado': 'y'})

        nome = f"tendencia_valor_agregado_{tipo.lower()}"
        if estado:
            nome += f"_e{estado}"
        if pais:
            nome += f"_p{pais}"
        return self.gerar_profecia(df_prophet, nome, f"Previsão de Valor Agregado médio de {tipo}", f"Valor Agregado médio {tipo} ($)")


    def tendencia_vlfob_ncm(self):
        return
    
    def tendencia_vlfob_setores(self):
        return
    
    def tendencia_ranking_ncm(self):
        return
    
    def tendencia_ranking_sh4(self):
        return
    
    def tendencia_ranking_setores(self):
        return

    # busca os ncm que mais aumentaram/diminuiram exportacao/importacao na série histórica
    def maiores_evolucoes_ncm(self):
        return
    
    # busca os sh4 que mais aumentaram/diminuiram exportacao/importacao na série histórica
    def maiores_evolucoes_sh4(self):
        return
