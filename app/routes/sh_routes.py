from flask import Blueprint, Response, json, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.dao import sh4_dao

from .routes_utils import get_args
from app.routes import routes_utils


sh_bp = Blueprint('sh', __name__)

limiter = Limiter(
    get_remote_address,  # Usa o IP do cliente para limitar requisições
    default_limits=["100 per hour"]  # Definição de um limite padrão
)


#rotas
#/busca_top_sh4_por_mun

@sh_bp.route('/busca_top_sh4_por_mun', methods=["GET"])
@limiter.limit("10 per minute")
def busca_top_sh4_por_mun():
    args = get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    top_sh4 = sh4_dao.busca_top_sh4_por_municipio(**args)

    if top_sh4 is not None:
        response = Response(
            json.dumps({'resposta': top_sh4}, ensure_ascii=False),  # Garante UTF-8
            content_type='application/json; charset=utf-8',
            status=200
        )
        return response

    return jsonify({'error': 'Ocorreu um erro inesperado ao buscar informações no banco de dados'}), 500


@sh_bp.route('/pesquisa_sh4_por_nome', methods=["GET"])
@limiter.limit("10 per minute")
def pesquisa_sh4_por_nome():
    nome = request.args.get('nome')
    if nome is None:
        pesquisa = sh4_dao.busca_todos_sh4()
    else:
        pesquisa = sh4_dao.pesquisa_sh4_por_nome(nome)
    return routes_utils.return_response(pesquisa)