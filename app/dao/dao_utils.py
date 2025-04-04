

def build_where(anos=None, meses=None, paises=None, estados=None, vias=None, urfs = None, municipios=None):
    filtros = []
    if anos:
        anos = [str(ano) for ano in anos]
        filtros.append(f"ano IN ({', '.join(anos)})")
    if meses:
        meses = [str(mes) for mes in meses]
        filtros.append(f"mes IN ({', '.join(meses)})")
    if paises:
        paises = [str(pais) for pais in paises]
        filtros.append(f"id_pais IN ({', '.join(paises)})")
    if estados:
        estados = [str(estado) for estado in estados]
        filtros.append(f"id_estado IN ({', '.join(estados)})")
    if vias:
        vias = [str(via) for via in vias]
        filtros.append(f"id_modal_transporte IN ({', '.join(vias)})")
    if urfs:
        urfs = [str(urf) for urf in urfs]
        filtros.append(f"id_unidade_receita_federal IN ({', '.join(urfs)})")

    if municipios:
        municipios = [str(municipio) for municipio in municipios]
        filtros.append(f"id_municipio IN ({', '.join(municipios)})")
    return f"WHERE {' AND '.join(filtros)}" if filtros else ""