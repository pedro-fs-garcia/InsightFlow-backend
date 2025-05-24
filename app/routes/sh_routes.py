from flask import Blueprint, Response, json, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.dao import sh4_dao
from app.dao.estado_dao import busca_estado_sigla
from app.estatisticas import sh4_stats

from .routes_utils import get_args
from app.routes import routes_utils


sh_bp = Blueprint('sh', __name__)

limiter = Limiter(
    get_remote_address,  # Usa o IP do cliente para limitar requisições
    default_limits=["100 per hour"]  # Definição de um limite padrão
)


@sh_bp.route('/busca_ranking_sh4', methods=["GET"])
def busca_top_sh4():
    args = get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    
    if 'tipo' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
    
    top_sh4 = sh4_dao.ranking_sh4(**args)
    return routes_utils.return_response(top_sh4)


@sh_bp.route('/pesquisa_sh4_por_nome', methods=["GET"])
@limiter.limit("10 per minute")
def pesquisa_sh4_por_nome():
    nome = request.args.get('nome')
    if nome is None:
        pesquisa = sh4_dao.busca_todos_sh4()
    else:
        pesquisa = sh4_dao.pesquisa_sh4_por_nome(nome)
    return routes_utils.return_response(pesquisa)


@sh_bp.route('/busca_vlfob_sh4', methods=["GET"])
def busca_vlfob_sh4():
    args = get_args(request)
    print(args)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if 'sh4' not in args.keys():
        return jsonify({'error':"Erro na requisição: parâmetro 'sh4' é obrigatório."}), 400

    vlfob_sh4 = sh4_dao.busca_vlfob_sh4(**args)
    return routes_utils.return_response(vlfob_sh4)


@sh_bp.route('/busca_tendencias_sh4', methods=["GET"])
def busca_tendencias_sh4():
    args = get_args(request)
    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if 'sh4' not in args.keys():
        return jsonify({'error':"Erro na requisição: parâmetro 'sh4' é obrigatório."}), 400

    if args.get('estado'):
        args['estado'] = busca_estado_sigla(args['estado'])
    if args.get('sh4'):
        args['sh4'] = str(args.get('sh4')[0])
    tendencias = sh4_stats.tendencia_sh4(**args)
    return routes_utils.return_response(tendencias)


@sh_bp.route('/busca_sh4_info', methods=["GET"])
def sh4_info():
    args = get_args(request)
    if 'sh4' not in args.keys():
        return jsonify({'error':"Erro na requisição: parâmetro 'sh4' é obrigatório."}), 400
    info = sh4_dao.busca_sh4_info(args.get('sh4'))
    return routes_utils.return_response(info)


@sh_bp.route('/busca_sh4_por_nome', methods=["GET"])
def busca_sh4_por_nome():
    nome = request.args.get('nome')
    if nome is None:
        pesquisa = sh4_dao.busca_todos_sh4()
    else:
        pesquisa = sh4_dao.pesquisa_sh4_por_nome(nome)
    return routes_utils.return_response(pesquisa)


@sh_bp.route('/busca_sh4_hist', methods=["GET"])
def busca_sh4_hist():
    args = routes_utils.get_args(request)
    print(args)
    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    args_keys = args.keys()
    if 'tipo' not in args_keys or 'sh4' not in args_keys:
        return jsonify({'error': "Erro na requisição: Parâmetros 'tipo' e 'sh4' são obrigatórios."}), 400

    hist_sh4 = sh4_dao.sh4_hist(**args)
    return routes_utils.return_response(hist_sh4)
