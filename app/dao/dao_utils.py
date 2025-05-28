

from typing import List


def build_where(
        anos:tuple[int,...]=None, 
        meses:tuple[int,...]=None, 
        paises:tuple[int,...]=None, 
        estados:tuple[int,...]=None, 
        vias:tuple[int,...]=None, 
        urfs:tuple[int,...]=None, 
        municipios:tuple[int,...]=None,
        ncm:tuple[int,...]=None,
) -> str:
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

    if ncm:
        if isinstance(ncm, int):
            ncm = [ncm]
        ncm = [str(id) for id in ncm]
        filtros.append(f"produto.id_ncm IN ({', '.join(ncm)})")

    return f"WHERE {' AND '.join(filtros)}" if filtros else ""