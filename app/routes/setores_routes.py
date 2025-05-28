from functools import cache
import json
import time
from typing import List
from app.dao.estado_dao import busca_estado_sigla
from data_pipeline.models.vidente import Vidente
from . import routes_utils
from flask import Blueprint, jsonify, request
import pandas as pd
from numpy import where
from ..utils.logging_config import error_logger, app_logger

setores_bp = Blueprint("setores", __name__)


#colunas: setor, DATA, SG_UF_NCM, CO_PAIS, VL_FOB_EXP, VL_FOB_IMP, KG_LIQUIDO_EXP, KG_LIQUIDO_IMP
@cache
def busca_vlfob_setores(anos:tuple[int,...]|None, pais:int|None, estado_sigla:str|None):
    inicio = time.time()
    try:
        app_logger.info("Iniciando carregamento do dataframe de setores")
        df_setores = pd.read_csv("data_pipeline/datasets/dados_agregados/mv_setores_mensal.csv")
    except:
        error_logger.error("Dataframe de setores não encontrado")
        df_setores = None
        
    if df_setores is not None:
        if estado_sigla:
            # estado_sigla = busca_estado_sigla(id_estado)
            df_setores = df_setores[df_setores['SG_UF_NCM'] == estado_sigla.upper()]
        if pais:
            df_setores = df_setores[df_setores['CO_PAIS'] == pais]
        if anos:
            df_setores = df_setores[pd.to_datetime(df_setores['DATA']).dt.year.isin(anos)]
        
        df_setores = df_setores.groupby('setor')[['VL_FOB_EXP', 'VL_FOB_IMP', 'KG_LIQUIDO_EXP', 'KG_LIQUIDO_IMP']].sum().reset_index()
        df_setores['valor_agregado_exp'] = where(df_setores['KG_LIQUIDO_EXP'] > 0, df_setores['VL_FOB_EXP'] / df_setores['KG_LIQUIDO_EXP'], 0)
        df_setores['valor_agregado_imp'] = where(df_setores['KG_LIQUIDO_IMP'] > 0, df_setores['VL_FOB_IMP'] / df_setores['KG_LIQUIDO_IMP'], 0)
        fim = time.time()
        tempo = f"Tempo de execução: {fim - inicio:.4f} segundos"
        app_logger.info(f"Informações por setores encontrados com sucesso. {tempo}")
        # df_setores = df_setores.sort_values(by='VL_FOB_EXP', ascending=False)
        return df_setores.to_dict(orient='records')
    return {}


@setores_bp.route("/busca_info_setores", methods=["GET"])
def busca_ranking_setores():
    args = routes_utils.get_args(request)
    
    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    
    res = busca_vlfob_setores(anos=args.get('anos'), 
                              pais=args.get('pais'), 
                              estado_sigla=args.get('estado_sigla')
                            )
    return routes_utils.return_response(res)