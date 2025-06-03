from functools import cache
import os
from typing import List, Literal
import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.statespace.sarimax import SARIMAX
import statsmodels.api as smapi
from pandas.tseries.offsets import MonthEnd
import warnings

from app.utils.logging_config import app_logger, error_logger


warnings.filterwarnings("ignore")


class Vidente():

    def gerar_profecia_json(self, df_prophet: pd.DataFrame, n_periods:int = 24):
        try : 
            if len(df_prophet) < 2:
                app_logger.info("Dados insuficientes para modelagem.")
                return df_prophet

            df = df_prophet.copy()
            df['ds'] = pd.to_datetime(df['ds'])
            df.set_index('ds', inplace=True)
            df = df.asfreq('MS')  #frequência mensal com início no início do mês
            df['y'] = df['y'].interpolate() 

            modelo = SARIMAX(df['y'], order=(1,1,1), seasonal_order=(1,1,0,12), enforce_stationarity=False, enforce_invertibility=False)
            modelo_fit = modelo.fit(disp=False)

            future_index = pd.date_range(start=df.index[-1] + MonthEnd(1), periods=n_periods, freq='MS')
            previsoes = modelo_fit.forecast(steps=n_periods)

            df_previsao = pd.concat([df['y'], pd.Series(previsoes, index=future_index)], axis=0)

            resultado = df_previsao.reset_index()
            resultado.columns = ['ds', 'yhat']
            resultado['ds'] = resultado['ds'].astype(str)

            app_logger.info(f"Análise de tendências finalizada")
            return resultado.to_dict(orient='records')
        except Exception as e:
            error_logger.error(f"Erro ao gerar previsão de tendência: {str(e)}")
            return None


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