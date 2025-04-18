from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..dao import estado_dao  # Supondo que exista um módulo estado_dao similar ao pais_dao
from .routes_utils import get_args
from app.routes import routes_utils


estado_bp = Blueprint('estado', __name__)

limiter = Limiter(
    get_remote_address,  # Usa o IP do cliente para limitar requisições
    default_limits=["100 per hour"]  # Definição de um limite padrão
)


# Rotas conforme especificado no README.md
# /ranking_estado
# /busca_estado_hist
# /pesquisa_estado_por_nome

@estado_bp.route('/ranking_estado', methods=["GET"])
@limiter.limit("10 per minute")
def busca_top_estados():
    args = get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    
    if 'tipo' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
    
    ranking_estado = estado_dao.busca_top_estado(**args)
    return routes_utils.return_response(ranking_estado)


@estado_bp.route('/busca_estado_hist', methods=["GET"])
@limiter.limit('10 per minute')
def busca_estado_hist():
    args = get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    args_keys = args.keys()
    if 'estados' not in args_keys or 'tipo' not in args_keys:
        return jsonify({'error': "Erro na requisição: Parâmetros 'tipo' e 'estados' são obrigatórios."}), 400
    
    estado_hist = estado_dao.busca_estado_hist(**args)
    return routes_utils.return_response(estado_hist)


@estado_bp.route('/pesquisa_estado_por_nome', methods=["GET"])
@limiter.limit('10 per minute')
def pesquisa_estado():
    nome = request.args.get('nome')
    if nome is None:
        pesquisa = estado_dao.busca_todos_estados()
    else:
        pesquisa = estado_dao.pesquisa_estado_por_nome(nome)
    return routes_utils.return_response(pesquisa)