
from flask import Response, jsonify, request, Blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from . import routes_utils
from ..dao import ncm_dao
from ..utils.logging_config import error_logger, app_logger

ncm_bp = Blueprint('ncm', __name__)

limiter = Limiter(
    get_remote_address,  # Usa o IP do cliente para limitar requisições
    default_limits=["100 per hour"]  # Definição de um limite padrão
)


#rotas
#/ranking_ncm
#/busca_por_ncm
#/busca_ncm_hist
#/busca_ncm_por_nome


@ncm_bp.route('/busca_transacoes_por_ncm', methods=['GET'])
@limiter.limit("10 per minute")
def busca_transacoes_por_ncm():
    args = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if 'tipo' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
        
    if 'ncm' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'ncm' é obrigatório."}), 400
    try:
        transacoes_ncm = ncm_dao.busca_transacoes_por_ncm(**args)
        return routes_utils.return_response(transacoes_ncm)
    except TypeError as e:
        error_logger.error(str(e))
        return jsonify({'error': f'Argumento inesperado na requisição: {str(e)}'}), 400


@ncm_bp.route('/ranking_ncm', methods=['GET'])
@limiter.limit("10 per minute")
def busca_top_ncm() -> Response:
    args = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if 'tipo' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400

    try:
        top_ncm = ncm_dao.busca_top_ncm(**args)
        return routes_utils.return_response(top_ncm)
    except TypeError as e:
        error_logger.error(str(e))
        return jsonify({'error': f'Argumento inesperado na requisição: {str(e)}'}), 400


@ncm_bp.route('/busca_por_ncm', methods=["GET"])
@limiter.limit('10 per minute')
def busca_por_ncm() -> Response:
    args = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    
    if 'ncm' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'ncm' é obrigatório."}), 400

    try:
        ncm_info = ncm_dao.busca_por_ncm(**args)
        return routes_utils.return_response(ncm_info)
    except TypeError as e:
        error_logger.error(str(e))
        return jsonify({'error': f'Argumento inesperado na requisição: {str(e)}'}), 400


@ncm_bp.route('/busca_ncm_hist', methods=["GET"])
@limiter.limit('10 per minute')
def busca_ncm_hist() -> Response:
    args = routes_utils.get_args(request)
    print(args)
    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    args_keys = args.keys()
    if 'tipo' not in args_keys or 'ncm' not in args_keys:
        return jsonify({'error': "Erro na requisição: Parâmetros 'tipo' e 'ncm' são obrigatórios."}), 400

    try:
        ncm_hist = ncm_dao.busca_ncm_hist(**args)
        return routes_utils.return_response(ncm_hist)
    except TypeError as e:
        error_logger.error(str(e))
        return jsonify({'error': f'Argumento inesperado na requisição: {str(e)}'}), 400
    

@ncm_bp.route("/pesquisa_ncm_por_nome", methods=["GET"])
@limiter.limit('10 per minute')
def pesquisa_ncm_por_nome():
    nome = request.args.get('nome')
    if nome is None:
        pesquisa = ncm_dao.busca_todos_ncm()
    else:
        pesquisa = ncm_dao.pesquisa_ncm_por_nome(nome)
    return routes_utils.return_response(pesquisa)
