from functools import cache
from typing import List, Literal
import pandas as pd
from psycopg2 import Error, OperationalError
from psycopg2.extras import DictCursor

from app.dao.dao_utils import build_where
from app.database.database_connection import get_connection
from app.estatisticas.stats_utils import historico_imp_exp_dataframe
from app.utils.logging_config import app_logger, error_logger


def dataframe_aux(tipo:str, ncm:List[int]=None, estados:List[int]=None, paises:List[int]=None):
    where_statement = build_where(paises=paises, estados=estados, ncm=ncm)
    where_statement = where_statement.replace("produto.id_ncm", "id_produto")
    query = f"""
        SELECT ano, mes, id_estado, id_pais, id_produto,
            SUM(valor_fob) as valor_fob
        FROM {tipo}ortacao_estado
        {where_statement}
        GROUP BY ano, mes, id_estado, id_pais, id_produto
    """
    print(query)
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query)
                res = cur.fetchall()
                app_logger.info("busca de hostórico de vlfob buscado para calculo de hhi")
                hist = [dict(row) for row in res]
    except (Error, OperationalError):
        error_logger.error("Erro ao buscar histórico de vlfob para cálculo de hhi")
        return pd.DataFrame(columns=['DATA', 'id_estado', 'id_pais', 'id_produto', f'valor_fob_{tipo}'])
    
    dict_filtrado = []
    for row in hist:
        dict_filtrado.append(
            {
                'ano': row.get('ano'),
                'mes': row.get('mes'),
                'id_estado': row.get('id_estado'),
                'id_pais': row.get('id_pais'),
                'id_produto': row.get('id_produto'),
                f'valor_fob_{tipo}':row.get('valor_fob')
            }
        )
    if not dict_filtrado: return pd.DataFrame(columns=['DATA', 'id_estado', 'id_pais', 'id_produto', f'valor_fob_{tipo}'])
    app_logger.info("Convertendo consulta para dataframe")
    df = pd.DataFrame(dict_filtrado)
    df[f'valor_fob_{tipo}'] = df[f'valor_fob_{tipo}'].astype(float)
    df['DATA'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2))
    df = df.drop(columns=['ano', 'mes'])
    df = df.fillna(0)
    app_logger.info("Fim do tratamento de dataframe")
    return df if len(df) > 0 else pd.DataFrame(columns=['DATA', 'id_estado', 'id_pais', 'id_produto', f'valor_fob_{tipo}'])


def dataframe_hhi(ncm:List[int]=None, estados:List[int]=None, paises:List[int]=None):
    hist_exp = dataframe_aux("exp", ncm, estados, paises)
    hist_imp = dataframe_aux("imp", ncm, estados, paises)
    merge_cols = ['DATA', 'id_pais', 'id_estado', 'id_produto']
    if hist_exp.empty and hist_imp.empty:
        return pd.DataFrame(columns=merge_cols + ['valor_fob_exp', 'valor_fob_imp'])
    app_logger.info("Juntando dataframes de exp e imp")
    hist = pd.merge(hist_exp, hist_imp, how="outer", on=merge_cols)
    hist.fillna(0, inplace=True)
    hist.sort_values('DATA', inplace=True)
    return hist


def analise_sazonalidade(df: pd.DataFrame):
    """
    Realiza análise de sazonalidade dos dados de exportação e importação,
    desconsiderando registros com valores zerados, e retorna dados para gráficos.
    """

    df['DATA'] = pd.to_datetime(df['DATA'])
    df['mes'] = df['DATA'].dt.month 

    # Filtra valores maiores que zero
    df_export = df[df['valor_fob_exp'] > 0]
    df_import = df[df['valor_fob_imp'] > 0]

    # Agrupa separadamente para evitar perda de dados relevantes
    exp_por_mes = df_export.groupby('mes')['valor_fob_exp'].sum()
    imp_por_mes = df_import.groupby('mes')['valor_fob_imp'].sum()

    # Junta os dois em um único DataFrame
    sazonalidade = pd.DataFrame({
        'valor_fob_exp': exp_por_mes,
        'valor_fob_imp': imp_por_mes
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
            'exportacoes': round(row['valor_fob_exp']/10, 2),
            'importacoes': round(row['valor_fob_imp']/10, 2),
        })

    return dados_json



def analise_hhi(crit: Literal["estado", "pais", "ncm"], df: pd.DataFrame):
    """
    Calcula o Índice Herfindahl-Hirschman (HHI) por mês, para exportações e importações,
    com base na concentração por país ou estado.
    """

    if crit not in ["estado", "pais", "ncm"]:
        raise ValueError("O critério deve ser 'estado' ou 'pais'.")

    if crit == 'estado':
        filtro = "id_estado"
    elif crit == 'pais':
        filtro = "id_pais"
    else:
        filtro = "id_produto"

    df['DATA'] = pd.to_datetime(df['DATA'])

    df_grouped = df.groupby([pd.Grouper(key='DATA', freq='MS'), filtro]).agg({
        'valor_fob_exp': 'sum',
        'valor_fob_imp': 'sum'
    }).reset_index()

    df_long = df_grouped.melt(
        id_vars=['DATA', filtro],
        value_vars=['valor_fob_exp', 'valor_fob_imp'],
        var_name='tipo',
        value_name='valor'
    )

    df_long['tipo'] = df_long['tipo'].map({
        'valor_fob_exp': 'exportacao',
        'valor_fob_imp': 'importacao'
    })

    df_long['total_mes'] = df_long.groupby(['DATA', 'tipo'])['valor'].transform('sum')
    df_long['participacao'] = df_long['valor'] / df_long['total_mes']

    df_hhi = df_long.groupby(['DATA', 'tipo'])['participacao'] \
        .apply(lambda x: (x**2).sum()).reset_index(name='hhi')

    df_hhi_pivot = df_hhi.pivot(index='DATA', columns='tipo', values='hhi').reset_index()
    df_hhi_pivot['mes'] = df_hhi_pivot['DATA'].dt.strftime('%Y-%m')

    df_hhi_pivot = df_hhi_pivot.fillna(0).sort_values('DATA')

    dados_json = df_hhi_pivot[['mes', 'exportacao', 'importacao']].rename(
        columns={'exportacao': 'hhi_exportacao', 'importacao': 'hhi_importacao'}
    ).round(4).to_dict(orient='records')

    return dados_json


@cache
def gerar_estatisticas_auxiliares(ncm:List[int]=None, estados:List[int]=None, paises:List[int]=None):
    """
    Gera todos os dados para o dashboard em um único JSON com todas as análises.
    """

    try:
        df = historico_imp_exp_dataframe(ncm, estados, paises)
        sazonalidade = analise_sazonalidade(df)
        
        # df = dataframe_hhi(ncm, estados, paises)
        from app import df_hhi
        df = df_hhi
        hhi_pais = analise_hhi(df=df, crit='pais')
        hhi_estado = analise_hhi(df=df, crit='estado')
        hhi_ncm = analise_hhi(df=df, crit='ncm')
        
        return {
            'sazonalidade': sazonalidade,
            'concentracao_pais': hhi_pais,
            'concentracao_estado': hhi_estado,
            'concentracao_ncm': hhi_ncm
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }