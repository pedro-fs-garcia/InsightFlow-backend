from app.dao.estado_dao import busca_estado_sigla
from data_pipeline.models.vidente import Vidente
from . import routes_utils
from flask import Blueprint, jsonify, request


tendencias_bp = Blueprint("tendencias", __name__)

vidente = Vidente()


@tendencias_bp.route('/busca_tendencia_balanca_comercial', methods=['GET'])
def busca_tendencia_balanca_comercial():
    args = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    if args.get('estado'):
        args['estado'] = busca_estado_sigla(args['estado'])
    balanca = vidente.tendencia_balanca_comercial(estado = args.get('estado'), pais=args.get('pais'))
    return routes_utils.return_response(balanca)


@tendencias_bp.route('/busca_tendencia_vlfob', methods=["GET"])
def busca_tendencia_vlfob():
    args:dict = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if 'tipo' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
    
    if args.get('tipo'):
        args['tipo'] = args['tipo'].upper()

    if args.get('estado'):
        args['estado'] = busca_estado_sigla(args['estado'])
    
    vlfob = vidente.tendencia_vlfob(
        tipo = args.get('tipo'),
        estado = args.get('estado'),
        pais = args.get('pais')
    )
    
    if isinstance(vlfob, str):
        return jsonify({'error': vlfob}), 403
    
    return routes_utils.return_response(vlfob)


@tendencias_bp.route('/busca_tendencia_va', methods=['GET'])
def busca_tendencia_va():
    args:dict = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if 'tipo' not in args.keys():
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
    
    if args.get('tipo'):
        args['tipo'] = args['tipo'].upper()

    if args.get('estado'):
        args['estado'] = busca_estado_sigla(args['estado'])
    
    va = vidente.tendencia_valor_agregado(
        tipo = args.get('tipo'),
        estado = args.get('estado'),
        pais = args.get('pais')
    )
    
    if isinstance(va, str):
        return jsonify({'error': va}), 403
    print(va)
    return routes_utils.return_response(va)