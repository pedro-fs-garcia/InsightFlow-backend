
from flask import Request, Response, json, jsonify, request, Blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..dao import ncm_dao
from . import routes_utils

ncm = Blueprint('ncm', __name__)

limiter = Limiter(
    get_remote_address,  # Usa o IP do cliente para limitar requisições
    default_limits=["100 per hour"]  # Definição de um limite padrão
)


@ncm.route('/busca_top_ncm', methods=['GET'])
@limiter.limit("10 per minute")
def busca_top_ncm() -> Response:
    args = routes_utils.get_args(request, False)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    top_ncm = ncm_dao.busca_top_ncm(**args)

    return routes_utils.return_response(top_ncm)


@ncm.route('/busca_por_ncm', methods=["GET"])
@limiter.limit('10 per minute')
def busca_por_ncm() -> Response:
    args = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    ncm_info = ncm_dao.busca_por_ncm(**args)

    return routes_utils.return_response(ncm_info)