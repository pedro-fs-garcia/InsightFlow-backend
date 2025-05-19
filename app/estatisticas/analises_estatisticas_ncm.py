from typing import Literal
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from app.dao.ncm_dao import busca_ncm_hist
from app.dao.transacao_dao import busca_dados_para_analise_hhi, busca_hist
from data_pipeline.models.vidente import Vidente


def dataframe_vlfob_ncm(tipo:Literal['exp', 'imp'], ncm:int|None = None, estado:int|None=None, pais:int|None=None):
    if estado: estado = (estado,)
    if pais: pais = (pais,)
    if ncm is None:
        ncm_hist = busca_hist(tipo=tipo, estado=estado, pais=pais)
    else:
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


def dataframe_balanca_ncm(ncm:int|None, estado:int|None=None, pais:int|None=None):
    if ncm : ncm = (ncm,)
    df_exp = dataframe_vlfob_ncm('exp', ncm=ncm, estado=estado, pais=pais)
    df_imp = dataframe_vlfob_ncm('imp', ncm=ncm, estado=estado, pais=pais)
    df = df_exp.merge(df_imp, how='outer', on = 'DATA').fillna(0)
    df['balanca_comercial'] = df['VL_FOB_EXP'] - df['VL_FOB_IMP']
    df = df.sort_values('DATA').reset_index(drop=False)
    # df = df.drop(columns=['VL_FOB_EXP', 'VL_FOB_IMP'])
    return df


def dataframe_hhi(crit:Literal['pais', 'estado', 'ncm'], ncm:int, estado:int|None=None, pais:int|None=None):
    print("\nfunc dataframe_hhi")
    print(f"pais: {pais}, estado:{estado}, ncm: {ncm}")
    exp = busca_dados_para_analise_hhi('exp', crit, ncm, estado, pais)
    imp = busca_dados_para_analise_hhi('imp', crit, ncm, estado, pais)
    df_exp = pd.DataFrame(exp or [])
    df_imp = pd.DataFrame(imp or [])
    if crit == 'estado':
        filtro = "id_estado"
    elif crit == 'pais':
        filtro = "id_pais"
    else:
        filtro = "id_produto"
    df = df_exp.merge(df_imp, how='outer', on=['ano', 'mes', filtro])
    df['DATA'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2))
    df = df.rename(columns={'vl_fob_exp': 'VL_FOB_EXP', 'vl_fob_imp': 'VL_FOB_IMP'})
    df = df.drop(columns=['ano', 'mes'])
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


def sazonalidade_ncm(ncm:int|None = None, estado:str|None=None, pais:str|None=None):
    df = dataframe_balanca_ncm(ncm, estado, pais)
    df['mes'] = df['DATA'].dt.month 

    # Filtra valores maiores que zero
    df_export = df[df['VL_FOB_EXP'] > 0]
    df_import = df[df['VL_FOB_IMP'] > 0]

    # Agrupa separadamente para evitar perda de dados relevantes
    exp_por_mes = df_export.groupby('mes')['VL_FOB_EXP'].sum()
    imp_por_mes = df_import.groupby('mes')['VL_FOB_IMP'].sum()

    # Junta os dois em um único DataFrame
    sazonalidade = pd.DataFrame({
        'VL_FOB_EXP': exp_por_mes,
        'VL_FOB_IMP': imp_por_mes
    }).fillna(0).reset_index()

    # Nome dos meses
    nome_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    sazonalidade['mes_nome'] = sazonalidade['mes'].apply(lambda x: nome_meses[x-1])

    # Monta JSON para gráfico
    dados_json = []
    for _, row in sazonalidade.iterrows():
        dados_json.append({
            'mes': row['mes_nome'],
            'exportacoes': round(row['VL_FOB_EXP']/10, 2),
            'importacoes': round(row['VL_FOB_IMP']/10, 2),
        })

    return dados_json


def analise_hhi_ncm(crit: Literal["estado", "pais", "ncm"], ncm: int | None = None, estado: str | None = None, pais: int | None = None):
    print("\nfunc analise_hhi_ncm")
    df = dataframe_hhi(crit, ncm, estado, pais)
    print(df.columns)
    print("\ndataframe de hhi criado com sucesso")
    if crit == 'estado':
        filtro = "id_estado"
    elif crit == 'pais':
        filtro = "id_pais"
    else:
        filtro = "id_produto"
    df_grouped = df.groupby([pd.Grouper(key='DATA', freq='MS'), filtro]).agg({
        'VL_FOB_EXP': 'sum',
        'VL_FOB_IMP': 'sum'
    }).reset_index()

    df_long = df_grouped.melt(
        id_vars=['DATA', filtro],
        value_vars=['VL_FOB_EXP', 'VL_FOB_IMP'],
        var_name='tipo',
        value_name='valor'
    )

    df_long['tipo'] = df_long['tipo'].map({
        'VL_FOB_EXP': 'exportacao',
        'VL_FOB_IMP': 'importacao'
    })
    df_long['total_mes'] = df_long.groupby(['DATA', 'tipo'])['valor'].transform('sum')
    df_long['total_mes'] = df_long['total_mes'].replace(0, np.nan)
    df_long['participacao'] = df_long['valor'] / df_long['total_mes']
    df_long['participacao'] = df_long['participacao'].fillna(0)
    # df_long['total_mes'] = df_long.groupby(['DATA', 'tipo'])['valor'].transform('sum')
    # df_long['participacao'] = df_long['valor'] / df_long['total_mes']

    df_hhi = df_long.groupby(['DATA', 'tipo'])['participacao'] \
        .apply(lambda x: (x**2).sum()).reset_index(name='hhi')

    df_hhi_pivot = df_hhi.pivot(index='DATA', columns='tipo', values='hhi').reset_index()
    df_hhi_pivot['mes'] = df_hhi_pivot['DATA'].dt.strftime('%Y-%m')

    df_hhi_pivot = df_hhi_pivot.fillna(0).sort_values('DATA')

    dados_json = df_hhi_pivot[['mes', 'exportacao', 'importacao']].rename(
        columns={'exportacao': 'hhi_exportacao', 'importacao': 'hhi_importacao'}
    ).round(4).to_dict(orient='records')

    return dados_json


def gerar_estatisticas_auxiliares_ncm(ncm:int|None = None, estado:str|None=None, pais:str|None=None):
    """
    Gera todos os dados para o dashboard em um único JSON com todas as análises.
    """

    try:
        sazonalidade = sazonalidade_ncm (ncm, estado, pais)
        print("sazonalidade: ", sazonalidade)
        hhi_pais = analise_hhi_ncm(pais=pais, estado=estado, ncm=ncm, crit='pais')
        print("\n\nhhi_pais: ", hhi_pais)
        hhi_estado = analise_hhi_ncm(pais=pais, estado=estado, ncm=ncm, crit='estado')
        print("\nhhi_estado: ", hhi_estado)
        hhi_ncm = analise_hhi_ncm(pais=pais, estado=estado, ncm=ncm, crit='ncm')
        return {
            'sazonalidade': sazonalidade,
            'concentracao_pais': hhi_pais,
            'concentracao_estado': hhi_estado,
            'concentracao_ncm': hhi_ncm
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e.with_traceback(None))
        }