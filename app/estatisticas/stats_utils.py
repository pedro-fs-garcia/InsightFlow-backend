import pandas as pd

def filtrar_df(
    df: pd.DataFrame,
    ncm: int = None,
    estado: str = None,
    pais: int = None,
    via: int = None,
    urf: int = None,
    sh4: str = None,
) -> pd.DataFrame:
    """
    Filtra um DataFrame de comércio exterior com base em múltiplos critérios opcionais.
    """
    if ncm is not None:
        df = df[df['CO_NCM'] == ncm]
    if estado is not None:
        df = df[df['SG_UF_NCM'] == estado]
    if pais is not None:
        df = df[df['CO_PAIS'] == pais]
    if via is not None:
        df = df[df['CO_VIA'] == via]
    if urf is not None:
        df = df[df['CO_URF'] == urf]
    if sh4 is not None:
        df = df[df['CO_SH4'] == sh4]
    return df
