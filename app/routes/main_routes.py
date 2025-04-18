from functools import cache
from flask import Blueprint, json, jsonify, request

from app.dao import sh4_dao, transacao_dao
from app.routes import routes_utils
from ..utils.logging_config import error_logger, app_logger

main = Blueprint ('main', __name__)


@main.route('/busca_transacao_por_id', methods=['GET'])
def main_function():
    args = routes_utils.get_args(request)
    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    if 'tipo' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
    if 'id_transacao' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
    
    try:
        tx = transacao_dao.busca_transacao_por_id(**args)
        return routes_utils.return_response(tx)
    except TypeError as e:
        error_logger.error(str(e))
        return jsonify({'error': f'Argumento inesperado na requisição: {str(e)}'}), 400
    

@main.route('/busca_vlfob_setores', methods=["GET"])
def busca_vlfob_setores():
    args = routes_utils.get_args(request)
    
    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    
    with open('app/static/setores.json') as json_file:
        setores = json.load(json_file)
    
    res = {}
    for setor, codes in setores.items():
        args['sh4'] = tuple(codes.get('sh4'))
        res[setor] = sh4_dao.busca_vlfob_sh4(**args)[0]
    return routes_utils.return_response(res)


from .ncm_routes import ncm_bp
from .bloco_routes import bloco_bp
from .pais_routes import pais_bp
from .sh_routes import sh_bp
from .bc_routes import balanca_comercial_bp
from .estados_routes import estado_bp

all_blueprints = [
    main, 
    ncm_bp, 
    pais_bp, 
    bloco_bp, 
    sh_bp, 
    balanca_comercial_bp,
    estado_bp
]