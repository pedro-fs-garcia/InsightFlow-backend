from . import routes_utils
from flask import Blueprint, jsonify, request

from app.dao import bc_dao



balanca_comercial_bp = Blueprint("balanca_comercial", __name__)


@balanca_comercial_bp.route("/busca_balanca_comercial", methods=["GET"])
def busca_balanca_comercial():
    args = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    balanca = bc_dao.busca_balanca_comercial(**args)
    return routes_utils.return_response(balanca)
