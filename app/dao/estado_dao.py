import time
from typing import List, Literal
from psycopg2 import Error
from psycopg2.extras import DictCursor

from .dao_utils import build_where
from ..database.database_connection import get_connection
from ..utils.logging_config import app_logger, error_logger


def busca_top_estado(
    tipo: Literal['exp', 'imp'],
    qtd: int = 26, 
    anos: List[int] = None, 
    meses: List[int] | None = None,
    ncm: List[int] | None = None,
    paises: List[int] | None = None,
    vias: List[int] | None = None,
    urfs: List[int] | None = None,
    crit: Literal['kg_liquido', 'valor_fob', 'valor_agregado', 'registros'] = 'valor_fob',
    cresc: Literal[1, 0] = 0
) -> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                where_statement = build_where(
                    anos=anos, paises=paises, meses=meses, vias=vias, urfs=urfs
                )

                if ncm:
                    filtro_ncm = f"id_produto IN ({', '.join(map(str, ncm))})"
                    where_statement += f" AND {filtro_ncm}" if where_statement else f"WHERE {filtro_ncm}"

                query = f"""
                    SELECT estado.id_estado,
                           estado.sigla AS sigla_estado,
                           estado.nome AS nome_estado,
                           SUM(valor_fob) as total_valor_fob,
                           SUM(kg_liquido) as total_kg_liquido,
                           CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado,
                           COUNT(*) AS total_registros
                    FROM {tipo}ortacao_estado 
                    JOIN estado ON {tipo}ortacao_estado.id_estado = estado.id_estado
                    {where_statement}
                    GROUP BY estado.id_estado, estado.sigla, estado.nome
                    ORDER BY total_{crit} {'ASC' if cresc else 'DESC'}
                    LIMIT %s
                """
                cur.execute(query, (qtd,))
                return [dict(row) for row in cur.fetchall()]
    except Error as e:
        error_logger.error(f'Erro ao buscar top estados: {str(e)}')
        return None


def busca_estado_hist(
        tipo: Literal['exp', 'imp'],
        estados: List[int],
        anos: List[int] | None = None,
        meses: List[int] | None = None,
        paises: List[int] | None = None,
        vias: List[int] | None = None,
        urfs: List[int] | None = None,
        ncm: List[int] | None = None,
) -> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                where_statement = build_where(anos=anos, meses=meses, estados=estados, paises=paises, vias=vias, urfs=urfs, ncm=ncm)
                where_statement = where_statement.replace('id_estado', f'{tipo}ortacao_estado.id_estado')

                query = f"""
                    SELECT estado.id_estado,
                        estado.sigla AS sigla_estado,
                        estado.nome AS nome_estado,
                        ano, mes,
                        SUM(kg_liquido) as kg_liquido_total_{tipo},
                        SUM(valor_fob) as valor_fob_total_{tipo},
                        CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS valor_agregado_total_{tipo},
                        COUNT(*) AS total_registros
                    FROM estado
                    LEFT JOIN {tipo}ortacao_estado ON estado.id_estado = {tipo}ortacao_estado.id_estado
                    {where_statement}
                    GROUP BY estado.id_estado, estado.sigla, estado.nome, ano, mes
                    ORDER BY ano, mes
                """
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
    except Error as e:
        error_logger.error(f"Erro ao buscar histórico dos estados: {str(e)}")
        return None


def pesquisa_estado_por_nome(nome: str) -> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query = """
                    SELECT id_estado, sigla, nome FROM estado
                    WHERE unaccent(nome) ILIKE unaccent(%s)
                    ORDER BY 
                        CASE 
                            WHEN nome ILIKE %s THEN 0
                            ELSE 1
                        END,
                        unaccent(nome)
                """
                cur.execute(query, (f"%{nome}%", f"{nome}%"))
                return [dict(row) for row in cur.fetchall()]
    except Error as e:
        error_logger.error(f"Erro ao pesquisar estados por nome: {str(e)}")
        return None


def busca_todos_estados():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT id_estado, sigla, nome FROM estado ORDER BY nome ASC")
                return [dict(row) for row in cur.fetchall()]
    except Error as e:
        error_logger.error("Erro ao buscar todos os estados.")
        return None