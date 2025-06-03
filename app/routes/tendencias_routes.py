from app.dao import sh4_dao
from app.dao.estado_dao import busca_estado_sigla
from app.estatisticas import sh4_stats, tendencias_stats
from app.estatisticas.analises_estatisticas_ncm import crescimento_mensal_balanca_ncm, crescimento_mensal_vlfob_ncm, previsao_tendencia_balanca_ncm, previsao_tendencia_va_ncm, previsao_tendencia_vlfob_ncm, regressao_linear_balanca_ncm, regressao_linear_vlfob_ncm, volatilidade_balanca_ncm, volatilidade_vlfob_ncm
from data_pipeline.models.analises_auxiliares import gerar_estatisticas_auxiliares_vlfob
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
    if args.get('ncm'):
        balanca = previsao_tendencia_balanca_ncm(ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))
    else:
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
    

    if args.get("ncm"):
        vlfob = previsao_tendencia_vlfob_ncm(tipo=args.get('tipo'), ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))
    else:
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
    

    if args.get('ncm'):
        va = previsao_tendencia_va_ncm(tipo=args.get('tipo'), ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))
    else:
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
    return routes_utils.return_response(va)


@tendencias_bp.route('/crescimento_mensal_vlfob', methods=["GET"])
def crescimento_mensal():
    args: dict = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if 'tipo' not in args:
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400

    if not args.get('ncm'):
        args['tipo'] = args['tipo'].upper()
        if args.get('estado'):
            args['estado'] = busca_estado_sigla(args['estado'])
        dados = vidente.crescimento_mensal_vlfob(
            tipo=args['tipo'],
            estado=args.get('estado'),
            pais=args.get('pais')
        )
    else:
        dados = crescimento_mensal_vlfob_ncm(tipo=args.get('tipo'), ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))
    return routes_utils.return_response(dados)


@tendencias_bp.route('/volatilidade_vlfob', methods=["GET"])
def volatilidade_vlfob():
    args: dict = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if 'tipo' not in args:
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400


    if args.get('ncm'):
        dados = volatilidade_vlfob_ncm(tipo=args.get('tipo'), ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))
    else:
        args['tipo'] = args['tipo'].upper()
        if args.get('estado'):
            args['estado'] = busca_estado_sigla(args['estado'])
        dados = vidente.volatilidade_vlfob(
            tipo=args['tipo'],
            estado=args.get('estado'),
            pais=args.get('pais')
        )

    return routes_utils.return_response(dados)


@tendencias_bp.route('/regressao_linear_vlfob', methods=["GET"])
def regressao_linear_vlfob():
    args: dict = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if 'tipo' not in args:
        return jsonify({'error': "Erro na requisição: Parâmetro 'tipo' é obrigatório."}), 400
    
    if args.get('ncm'):
        dados = regressao_linear_vlfob_ncm(tipo=args.get('tipo'), ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))

    else:
        args['tipo'] = args['tipo'].upper()
        if args.get('estado'):
            args['estado'] = busca_estado_sigla(args['estado'])
        dados = vidente.regressao_linear_vlfob(
            tipo=args.get('tipo'),
            estado=args.get('estado'),
            pais=args.get('pais')
        )
    return routes_utils.return_response(dados)


@tendencias_bp.route('/regressao_linear_balanca_comercial', methods=["GET"])
def regressao_linear_balanca_comercial():
    args: dict = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if args.get('ncm'):
        dados = regressao_linear_balanca_ncm(ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))
    else:
        if args.get('estado'):
            args['estado'] = busca_estado_sigla(args['estado'])
        dados = vidente.regressao_linear_balanca_comercial(
            estado=args.get('estado'),
            pais=args.get('pais')
        )

    return routes_utils.return_response(dados)


@tendencias_bp.route('/crescimento_mensal_balanca_comercial', methods=["GET"])
def crescimento_mensal_balanca_comercial():
    args: dict = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if args.get('ncm'):
        dados = crescimento_mensal_balanca_ncm(ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))
    else:
        if args.get('estado'):
            args['estado'] = busca_estado_sigla(args['estado'])

        dados = vidente.crescimento_mensal_balanca_comercial(
            estado=args.get('estado'),
            pais=args.get('pais')
        )
    return routes_utils.return_response(dados)


@tendencias_bp.route('/volatilidade_balanca_comercial', methods=["GET"])
def volatilidade_balanca_comercial():
    args: dict = routes_utils.get_args(request)

    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400
    
    if args.get('ncm'):
        dados = volatilidade_balanca_ncm(ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))
    else:
        if args.get('estado'):
            args['estado'] = busca_estado_sigla(args['estado'])

        dados = vidente.volatilidade_balanca_comercial(
            estado=args.get('estado'),
            pais=args.get('pais')
        )
    return routes_utils.return_response(dados)


@tendencias_bp.route('/estatisticas_auxiliares_vlfob', methods=["GET"])
def estatisticas_auxiliares_vlfob():
    args: dict = routes_utils.get_args(request)
    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    if args.get('estado'):
        args['estado'] = busca_estado_sigla(args['estado'])
    
    dados = gerar_estatisticas_auxiliares_vlfob(
        ncm = args.get('ncm'),
        estado = args.get('estado'),
        pais=args.get('pais')
    )
    return routes_utils.return_response(dados)


@tendencias_bp.route('/busca_tendencias_dashboard', methods=['GET'])
def busca_tendencia_sh4():
    args = routes_utils.get_args(request)
    if not isinstance(args, dict):
        return jsonify({'error': f'Erro na requisição: {args}'}), 400

    # if args.get('sh4'):
    #     args['sh4'] = str(args.get('sh4')[0])
    if args.get('ncm'):
        args['ncm'] = int(args.get('ncm')[0])

    if args.get('sh4'):
        tendencias = sh4_stats.tendencia_sh4(sh4=args.get('sh4'), estado=args.get('estado'), pais=args.get('pais'))
        print(args)
        # tendencias = sh4_dao.sh4_hist(**args)
    else:
        tendencias = tendencias_stats.tendencias_dashboard(ncm=args.get('ncm'), estado=args.get('estado'), pais=args.get('pais'))
    
    return routes_utils.return_response(tendencias)