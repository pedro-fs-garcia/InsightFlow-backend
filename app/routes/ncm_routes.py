from flask import Response, json, jsonify, request, Blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.dao import ncm_dao
from app.dao.ncm_dao import busca_top_ncm

ncm = Blueprint('ncm', __name__)


limiter = Limiter(
    get_remote_address,  # Usa o IP do cliente para limitar requisições
    default_limits=["100 per hour"]  # Definição de um limite padrão
)


@ncm.route('/busca_top_ncm', methods=['GET'])
@limiter.limit("10 per minute")
def busca_top_ncm():
    errors = []
    args = {
        "tipo" : request.args.get('tipo', type=str),
        "qtd" : request.args.get('qtd', type=int),
        "anos" : request.args.getlist('anos', type=int),
        "meses" : request.args.getlist('meses', type=int),
        "paises" : request.args.getlist('paises', type=int),
        "estados" : request.args.getlist('estados', type=int),
        "vias" : request.args.getlist('vias', type=int),
        "crit" : request.args.get('crit', type=str)
    }

    print(args.get('anos'))

    tipo = args['tipo']
    if tipo is not None and tipo not in ['exp', 'imp']:
        errors.append("Tipo de transação deve ser 'exp' ou 'imp'.")

    qtd = args['qtd']
    if qtd is not None and qtd <= 0:
        errors.append('Quantidade informada deve ser um número inteiro positivo.')

    anos = args.get('anos')
    for ano in anos:
        if ano not in range(2014, 2025):
            errors.append(f'Ano inválido: {ano}. Utilize um ano entre 2014 e 2024.')
            break
    
    crit = args.get('crit')
    criterios_validos = {'kg_liquido', 'valor_fob', 'valor_agregado', 'registros'}
    if crit and crit not in criterios_validos:
        errors.append(f"Critério de ordenação inválido. Utilize um dos critérios válidos: {', '.join(criterios_validos)}.")

    if errors:
        return jsonify({'error': f'Erro na requisição: {errors}'}), 400
    
    if qtd is None: args['qtd'] = 10
    if crit is None: args['crit'] = 'valor_fob'

    top_ncm = ncm_dao.busca_top_ncm(**args)

    if top_ncm is not None:
        response = Response(
            json.dumps({'resposta': top_ncm}, ensure_ascii=False),  # Garante UTF-8
            content_type='application/json; charset=utf-8',
            status=200
        )
        return response

    return jsonify({'error': 'Ocorreu um erro inesperado ao buscar informações no banco de dados'}), 500
