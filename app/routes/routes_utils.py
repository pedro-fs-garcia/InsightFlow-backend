from flask import Request


def get_args(request: Request, por_mun:bool) -> dict | list:
    errors = []
    args = {
        "tipo" : request.args.get('tipo', type=str),
        "qtd" : request.args.get('qtd', type=int),
        "anos" : request.args.getlist('anos', type=int),
        "meses" : request.args.getlist('meses', type=int),
        "paises" : request.args.getlist('paises', type=int),
        "crit" : request.args.get('crit', type=str)
    }

    if por_mun:
        args["municipios"] = request.args.getlist('municipios', type=int)
    else:
        args["estados"] = request.args.getlist('estados', type=int)
        args["vias"] = request.args.getlist('vias', type=int)
        args["urfs"] = request.args.getlist('urfs', type=int)
    
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
        return errors
    
    if qtd is None: args['qtd'] = 10
    if crit is None: args['crit'] = 'valor_fob'

    return args