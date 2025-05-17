from functools import cache
import json
import os
from typing import List, Literal
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.statespace.sarimax import SARIMAX
import statsmodels.api as smapi
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
        
        # plt.figure(figsize=(10, 5))
        # df_previsao.plot(label='Previsão')
        # plt.axvline(df.index[-1], color='gray', linestyle='--', label='Início da previsão')
        # plt.title(titulo_graf)
        # plt.xlabel('Data')
        # plt.ylabel(ylabel)
        # plt.legend()
        # plt.grid(True)
        # plt.tight_layout()
        # plt.savefig(f'{self.output_dir}/{nome_arquivo}.png', dpi=300)
        # plt.close()

        resultado = df_previsao.reset_index()
        resultado.columns = ['ds', 'yhat']
        resultado['ds'] = resultado['ds'].astype(str)

        app_logger.info(f"Análise de tendências {nome_arquivo} finalizada")
        return resultado.to_dict(orient='records')


    @cache
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
        df_prophet['y'] = df_prophet['y'].fillna(0)

        nome = f"tendencia_balanca_comercial"
        if estado:
            nome += f"_e{estado}"
        if pais:
            nome += f"_p{pais}"
        return self.gerar_profecia(df_prophet, nome, f"Previsão de Balança Comercial", "Balança Comercial ($)")

    @cache
    def regressao_linear_balanca_comercial(self, estado: str | None = None, pais: int | None = None) -> dict:
        df = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_balanca_comercial.csv")
        if estado:
            df = df[df['SG_UF_NCM'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]
        df = df.groupby('DATA')[[f'balanca_comercial']].sum().reset_index()
        df['DATA'] = pd.to_datetime(df['DATA'])
        df = df.sort_values('DATA')
        df['timestamp'] = df['DATA'].map(pd.Timestamp.timestamp)
        X = df[['timestamp']]
        y = df[f'balanca_comercial']
        modelo = LinearRegression()
        modelo.fit(X, y)
        previsoes = modelo.predict(X)
        df_resultado = pd.DataFrame({
            'ds': df['DATA'].astype(str),
            'y_real': y,
            'y_regressao': previsoes
        })
        return {
            "dados": df_resultado.to_dict(orient='records'),
            "coeficiente_angular": modelo.coef_[0],
            "intercepto": modelo.intercept_,
            "r2": modelo.score(X, y)
        }
    

    @cache
    def crescimento_mensal_balanca_comercial(self, estado: str | None = None, pais: int | None = None) -> List[dict]:
        df = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_balanca_comercial.csv")
        if estado:
            df = df[df['SG_UF_NCM'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]
        df = df.groupby('DATA')[[f'balanca_comercial']].sum().reset_index()
        df['DATA'] = pd.to_datetime(df['DATA'])
        df = df.sort_values('DATA')
        df['crescimento'] = df[f'balanca_comercial'].pct_change().fillna(0) * 100
        df_resultado = df[['DATA', 'crescimento']].rename(columns={'DATA': 'ds', 'crescimento': 'y'})
        # df_resultado['ds'] = df_resultado['ds'].astype(str)
        # return df_resultado.to_dict(orient='records')
        nome = f"tendencia_crescimento_mensal_balanca"
        if estado:
            nome += f"_e{estado}"
        if pais:
            nome += f"_p{pais}"
        return self.gerar_profecia(df_resultado, nome, "Crescimento Mensal da balança comercial", f"Taxa de crescimento")


    @cache
    def volatilidade_balanca_comercial(self, estado: str | None = None, pais: int | None = None) -> List[dict]:
        df = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_balanca_comercial.csv")
        if estado:
            df = df[df['SG_UF_NCM'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]
        df = df.groupby('DATA')[[f'balanca_comercial']].sum().reset_index()
        df['DATA'] = pd.to_datetime(df['DATA'])
        df = df.sort_values('DATA')
        df['volatilidade'] = df[f'balanca_comercial'].rolling(window=6).std().fillna(0)
        df_resultado = df[['DATA', 'volatilidade']].rename(columns={'DATA': 'ds', 'volatilidade': 'y'})
        # df_resultado['ds'] = df_resultado['ds'].astype(str)
        # return df_resultado.to_dict(orient='records')
        nome = f"tendencia_volatilidade_balanca"
        if estado:
            nome += f"_e{estado}"
        if pais:
            nome += f"_p{pais}"
        return self.gerar_profecia(df_resultado, nome, "Volatilidade da Balança Comercial", f"Volatiliade")



    @cache
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
        df_prophet['y'] = df_prophet['y'].fillna(0)

        nome = f"tendencia_vlfob_{tipo.lower()}"
        if estado:
            nome += f"_e{estado}"
        if pais:
            nome += f"_p{pais}"
        return self.gerar_profecia(df_prophet, nome, f"Previsão de Valor Fob de {tipo}", f"Valor Fob {tipo} ($)")
    

    @cache
    def crescimento_mensal_vlfob(self, tipo: Literal['EXP', 'IMP'], estado: str | None = None, pais: int | None = None) -> List[dict]:
        df = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_balanca_comercial.csv")
        if estado:
            df = df[df['SG_UF_NCM'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]
        df = df.groupby('DATA')[[f'VL_FOB_{tipo}']].sum().reset_index()
        df['DATA'] = pd.to_datetime(df['DATA'])
        df = df.sort_values('DATA')
        df['crescimento'] = df[f'VL_FOB_{tipo}'].pct_change().fillna(0) * 100
        df_resultado = df[['DATA', 'crescimento']].rename(columns={'DATA': 'ds', 'crescimento': 'y'})
        # df_resultado['ds'] = df_resultado['ds'].astype(str)
        # return df_resultado.to_dict(orient='records')
        nome = f"tendencia_crescimento_mensal_vlfob_{tipo.lower()}"
        if estado:
            nome += f"_e{estado}"
        if pais:
            nome += f"_p{pais}"
        return self.gerar_profecia(df_resultado, nome, "Crescimento Mensal do Valor Fob", f"Taxa de crescimento {tipo}")


    @cache
    def volatilidade_vlfob(self, tipo: Literal['EXP', 'IMP'], estado: str | None = None, pais: int | None = None) -> List[dict]:
        df = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_balanca_comercial.csv")
        if estado:
            df = df[df['SG_UF_NCM'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]
        df = df.groupby('DATA')[[f'VL_FOB_{tipo}']].sum().reset_index()
        df['DATA'] = pd.to_datetime(df['DATA'])
        df = df.sort_values('DATA')
        df['volatilidade'] = df[f'VL_FOB_{tipo}'].rolling(window=6).std().fillna(0)
        df_resultado = df[['DATA', 'volatilidade']].rename(columns={'DATA': 'ds', 'volatilidade': 'y'})
        # df_resultado['ds'] = df_resultado['ds'].astype(str)
        # return df_resultado.to_dict(orient='records')
        nome = f"tendencia_volatilidade_vlfob_{tipo.lower()}"
        if estado:
            nome += f"_e{estado}"
        if pais:
            nome += f"_p{pais}"
        return self.gerar_profecia(df_resultado, nome, "Volatilidade de Valor FOB", f"Volatiliade {tipo}")


    @cache
    def regressao_linear_vlfob(self, tipo: Literal['EXP', 'IMP'], estado: str | None = None, pais: int | None = None) -> dict:
        df = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_balanca_comercial.csv")
        if estado:
            df = df[df['SG_UF_NCM'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]
        df = df.groupby('DATA')[[f'VL_FOB_{tipo}']].sum().reset_index()
        df['DATA'] = pd.to_datetime(df['DATA'])
        df = df.sort_values('DATA')
        df['timestamp'] = df['DATA'].map(pd.Timestamp.timestamp)
        X = df[['timestamp']]
        y = df[f'VL_FOB_{tipo}']
        modelo = LinearRegression()
        modelo.fit(X, y)
        previsoes = modelo.predict(X)
        df_resultado = pd.DataFrame({
            'ds': df['DATA'].astype(str),
            'y_real': y,
            'y_regressao': previsoes
        })
        return {
            "dados": df_resultado.to_dict(orient='records'),
            "coeficiente_angular": modelo.coef_[0],
            "intercepto": modelo.intercept_,
            "r2": modelo.score(X, y)
        }


    @cache
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
        df_prophet['y'] = df_prophet['y'].fillna(0)

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

    # busca os ncm que mais aumentaram/diminuiram exportacao/importacao na série histórica
    def maiores_evolucoes_ncm(self):
        return
    
    # busca os sh4 que mais aumentaram/diminuiram exportacao/importacao na série histórica
    def maiores_evolucoes_sh4(self):
        return
