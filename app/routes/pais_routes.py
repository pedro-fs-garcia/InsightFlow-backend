from flask import Blueprint, Response, json, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..dao import pais_dao

from .routes_utils import get_args
from app.routes import routes_utils


pais_bp = Blueprint('pais', __name__)

limiter = Limiter(
    get_remote_address,  # Usa o IP do cliente para limitar requisições
    default_limits=["100 per hour"]  # Definição de um limite padrão
)


#rotas
# /ranking_pais
# /busca_pais_hist
#/busca_pais_por_nome

@pais_bp.route('/ranking_pais', methods = ["GET"])
@limiter.limit("10 per minute")
def busca_top_paises():
    args = get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    
    if 'tipo' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
    
    ranking_pais = pais_dao.busca_top_pais(**args)
    return routes_utils.return_response(ranking_pais)


@pais_bp.route('/busca_pais_hist', methods=["GET"])
@limiter.limit('10 per minute')
def busca_pais_hist():
    args = get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    args_keys = args.keys()
    if 'paises' not in args_keys or 'tipo' not in args_keys:
        return jsonify({'error': "Erro na requisição: Parâmetros 'tipo' e 'paises' são obrigatórios."}), 400
    
    pais_hist = pais_dao.busca_pais_hist(**args)
    return routes_utils.return_response(pais_hist)


@pais_bp.route('/busca_pais_exp_imp_info', methods=["GET"])
def busca_pais_exp_imp_info():
    args = get_args(request)
    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    args_keys = args.keys()
    if 'paises' not in args_keys:
        return jsonify({'error': "Erro na requisição: Parâmetro 'paises' é obrigatório."}), 400
    
    pais_info = pais_dao.busca_pais_exp_imp_info(**args)
    return routes_utils.return_response(pais_info)


@pais_bp.route('/pesquisa_pais_por_nome', methods=["GET"])
@limiter.limit('10 per minute')
def pesquisa_pais():
    nome = request.args.get('nome')
    if nome is None:
        pesquisa = pais_dao.busca_todos_paises()
    else:
        pesquisa = pais_dao.pesquisa_pais_por_nome(nome)
    return routes_utils.return_response(pesquisa)