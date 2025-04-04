from flask import Blueprint, Response, json, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..dao import pais_dao

from .routes_utils import get_args
from app.routes import routes_utils


pais = Blueprint('pais', __name__)

limiter = Limiter(
    get_remote_address,  # Usa o IP do cliente para limitar requisições
    default_limits=["100 per hour"]  # Definição de um limite padrão
)


#rotas
# /ranking_pais

@pais.route('/ranking_pais', methods = ["GET"])
@limiter.limit("10 per minute")
def busca_top_paises():
    args = get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    
    ranking_pais = pais_dao.busca_top_pais(**args)

    return routes_utils.return_response(ranking_pais)