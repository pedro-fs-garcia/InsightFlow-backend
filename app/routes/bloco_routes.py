from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..dao import bloco_dao
from .routes_utils import get_args
from app.routes import routes_utils
from app.utils.logging_config import app_logger, error_logger
from typing import Literal


bloco_bp = Blueprint('bloco', __name__)

limiter = Limiter(
    get_remote_address,  # Usa o IP do cliente para limitar requisições
    default_limits=["100 per hour"]  # Definição de um limite padrão
)


#rotas
# /ranking_blocos
# /pesquisa_bloco_por_nome

@bloco_bp.route('/ranking_bloco', methods=['GET'])
@limiter.limit('10 per minute')
def busca_top_blocos():
    args = get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    
    if 'tipo' not in args.keys():   
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
        
    ranking_blocos = bloco_dao.busca_top_bloco(**args)
    return routes_utils.return_response(ranking_blocos)


@bloco_bp.route('/pesquisa_bloco_por_nome', methods=['GET'])
@limiter.limit('10 per minute')
def pesquisa_bloco():
    nome = request.args.get('nome')
    if nome is None:
        pesquisa = bloco_dao.busca_todos_blocos()
    else:
        pesquisa = bloco_dao.pesquisa_bloco_por_nome(nome)
    return routes_utils.return_response(pesquisa)
