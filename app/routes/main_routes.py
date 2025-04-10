from flask import Blueprint, jsonify, request

from app.dao import transacao_dao
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

from .ncm_routes import ncm_bp
from .bloco_routes import bloco_bp
from .pais_routes import pais_bp
from .sh_routes import sh_bp
from .bc_routes import balanca_comercial_bp

all_blueprints = [
    main, 
    ncm_bp, 
    pais_bp, 
    bloco_bp, 
    sh_bp, 
    balanca_comercial_bp
]