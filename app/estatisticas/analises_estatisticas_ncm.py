from typing import Literal
import pandas as pd
from sklearn.linear_model import LinearRegression

from app.dao.ncm_dao import busca_ncm_hist
from data_pipeline.models.vidente import Vidente


def dataframe_vlfob_ncm(tipo:Literal['exp', 'imp'], ncm:int, estado:int|None=None, pais:int|None=None):
    if estado: estado = (estado,)
    if pais: pais = (pais,)
    ncm_hist = busca_ncm_hist(tipo=tipo, ncm=ncm, estados=estado, paises=pais)
    if len(ncm_hist) < 1:
        return None
    tipo = tipo.upper()
    ncm_dict_filtrado = []
    for row in ncm_hist:
        ncm_dict_filtrado.append(
            {
                'ano': row.get('ano'),
                'mes': row.get('mes'),
                f'VL_FOB_{tipo.upper()}':row.get('total_valor_fob')
            }
        )
    df = pd.DataFrame(ncm_dict_filtrado)
    df[f'VL_FOB_{tipo.upper()}'] = df[f'VL_FOB_{tipo.upper()}'].astype(float)
    df['DATA'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2))
    df = df.drop(columns=['ano', 'mes'])
    return df


def dataframe_balanca_ncm(ncm:int, estado:int|None=None, pais:int|None=None):
    df_exp = dataframe_vlfob_ncm('exp', ncm=ncm, estado=estado, pais=pais)
    df_imp = dataframe_vlfob_ncm('imp', ncm=ncm, estado=estado, pais=pais)
    df = df_exp.merge(df_imp, how='outer', on = 'DATA').fillna(0)
    df['balanca_comercial'] = df['VL_FOB_EXP'] - df['VL_FOB_IMP']
    df = df.sort_values('DATA').reset_index(drop=True)
    df = df.drop(columns=['VL_FOB_EXP', 'VL_FOB_IMP'])
    return df

def dataframe_va_ncm(tipo:Literal['exp', 'imp'], ncm:int, estado:int|None=None, pais:int|None=None):
    if estado: estado = (estado,)
    if pais: pais = (pais,)
    ncm_hist = busca_ncm_hist(tipo=tipo, ncm=ncm, estados=estado, paises=pais)
    if len(ncm_hist) < 1:
        return None
    tipo = tipo.upper()
    ncm_dict_filtrado = []
    for row in ncm_hist:
        ncm_dict_filtrado.append(
            {
                'ano': row.get('ano'),
                'mes': row.get('mes'),
                f'VL_FOB_{tipo.upper()}':row.get('total_valor_fob'),
                f'KG_LIQUIDO_{tipo}': row.get('total_kg_liquido')
            }
        )
    df = pd.DataFrame(ncm_dict_filtrado)
    df[f'VL_FOB_{tipo.upper()}'] = df[f'VL_FOB_{tipo.upper()}'].astype(float)
    df[f'KG_LIQUIDO_{tipo.upper()}'] = df[f'KG_LIQUIDO_{tipo.upper()}'].astype(float)
    df['DATA'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2))
    df = df.drop(columns=['ano', 'mes'])
    return df


def previsao_tendencia_vlfob_ncm (tipo:Literal['exp', 'imp'], ncm:int, estado:int|None=None, pais:int|None=None):
    df = dataframe_vlfob_ncm(tipo, ncm, estado, pais)
    df = df.groupby('DATA')[[f'VL_FOB_{tipo}']].sum().reset_index()
    df_prophet = df[['DATA', f'VL_FOB_{tipo}']].rename(columns={'DATA': 'ds', f'VL_FOB_{tipo}': 'y'})
    df_prophet['y'] = df_prophet['y'].fillna(0)
    nome = f"tendencia_vlfob_{tipo.lower()}"
    if estado:
        nome += f"_e{estado}"
    if pais:
        nome += f"_p{pais}"
    vidente = Vidente()
    return vidente.gerar_profecia(df_prophet, nome, f"Previsão de Valor Fob de {tipo}", f"Valor Fob {tipo} ($)")


def previsao_tendencia_balanca_ncm(ncm:int, estado:int|None=None, pais:int|None=None):
    df = dataframe_balanca_ncm(ncm, estado, pais)
    df = df.groupby('DATA')[['balanca_comercial']].sum().reset_index()
    df_prophet = df[['DATA', 'balanca_comercial']].rename(columns={'DATA': 'ds', 'balanca_comercial': 'y'})
    df_prophet['y'] = df_prophet['y'].fillna(0)

    nome = f"tendencia_balanca_comercial"
    if estado:
        nome += f"_e{estado}"
    if pais:
        nome += f"_p{pais}"
    vidente = Vidente()
    return vidente.gerar_profecia(df_prophet, nome, f"Previsão de Balança Comercial", "Balança Comercial ($)")


def previsao_tendencia_va_ncm(tipo:Literal['exp', 'imp'], ncm:int, estado:int|None=None, pais:int|None=None):
    df = dataframe_va_ncm(tipo, ncm, estado, pais)
    df = df.groupby('DATA')[[f'VL_FOB_{tipo}', f'KG_LIQUIDO_{tipo}']].sum().reset_index()
    df['valor_agregado'] = df[f'VL_FOB_{tipo}'] / df[f'KG_LIQUIDO_{tipo}']
    df_prophet = df[['DATA', 'valor_agregado']].rename(columns={'DATA': 'ds', 'valor_agregado': 'y'})
    df_prophet['y'] = df_prophet['y'].fillna(0)
    nome = f"tendencia_valor_agregado_{tipo.lower()}"
    if estado:
        nome += f"_e{estado}"
    if pais:
        nome += f"_p{pais}"
    vidente = Vidente()
    return vidente.gerar_profecia(df_prophet, nome, f"Previsão de Valor Agregado médio de {tipo}", f"Valor Agregado médio {tipo} ($)")



def regressao_linear_vlfob_ncm(tipo:Literal['exp', 'imp'], ncm:int, estado:int|None=None, pais:int|None=None):
    df = dataframe_vlfob_ncm(tipo, ncm, estado, pais)
    tipo = tipo.upper()
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


def crescimento_mensal_vlfob_ncm(tipo:Literal['exp', 'imp'], ncm:int, estado:int|None=None, pais:int|None=None):
    df = dataframe_vlfob_ncm(tipo, ncm, estado, pais)
    tipo = tipo.upper()
    df['crescimento'] = df[f'VL_FOB_{tipo}'].pct_change().fillna(0) * 100
    df_resultado = df[['DATA', 'crescimento']].rename(columns={'DATA': 'ds', 'crescimento': 'y'})
    nome = f"tendencia_crescimento_mensal_vlfob_{tipo.lower()}"
    if estado:
        nome += f"_e{estado}"
    if pais:
        nome += f"_p{pais}"
    vidente = Vidente()
    return vidente.gerar_profecia(df_resultado, nome, "Crescimento Mensal do Valor Fob", f"Taxa de crescimento {tipo}")


def volatilidade_vlfob_ncm(tipo:Literal['exp', 'imp'], ncm:int, estado:int|None=None, pais:int|None=None):
    df = dataframe_vlfob_ncm(tipo, ncm, estado, pais)
    if df is None: return None
    tipo = tipo.upper()
    df['volatilidade'] = df[f'VL_FOB_{tipo}'].rolling(window=6).std().fillna(0)
    df_resultado = df[['DATA', 'volatilidade']].rename(columns={'DATA': 'ds', 'volatilidade': 'y'})
    nome = f"tendencia_volatilidade_vlfob_{tipo.lower()}"
    if estado:
        nome += f"_e{estado}"
    if pais:
        nome += f"_p{pais}"
    vidente = Vidente()
    return vidente.gerar_profecia(df_resultado, nome, "Volatilidade de Valor FOB", f"Volatiliade {tipo}")


def regressao_linear_balanca_ncm(ncm:int, estado:int|None=None, pais:int|None=None):
    df = dataframe_balanca_ncm(ncm, estado, pais)
    if df is None: return None
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


def crescimento_mensal_balanca_ncm(ncm:int, estado:int|None=None, pais:int|None=None):
    df = dataframe_balanca_ncm(ncm, estado, pais)
    df['crescimento'] = df[f'balanca_comercial'].pct_change().fillna(0) * 100
    df_resultado = df[['DATA', 'crescimento']].rename(columns={'DATA': 'ds', 'crescimento': 'y'})
    nome = f"tendencia_crescimento_mensal_balanca"
    if estado:
        nome += f"_e{estado}"
    if pais:
        nome += f"_p{pais}"
    vidente = Vidente()
    return vidente.gerar_profecia(df_resultado, nome, "Crescimento Mensal da balança comercial", f"Taxa de crescimento")


def volatilidade_balanca_ncm(ncm:int, estado:int|None=None, pais:int|None=None):
    df = dataframe_balanca_ncm(ncm, estado, pais)
    df['volatilidade'] = df[f'balanca_comercial'].rolling(window=6).std().fillna(0)
    df_resultado = df[['DATA', 'volatilidade']].rename(columns={'DATA': 'ds', 'volatilidade': 'y'})
    nome = f"tendencia_volatilidade_balanca"
    if estado:
        nome += f"_e{estado}"
    if pais:
        nome += f"_p{pais}"
    vidente = Vidente()
    return vidente.gerar_profecia(df_resultado, nome, "Volatilidade da Balança Comercial", f"Volatiliade")