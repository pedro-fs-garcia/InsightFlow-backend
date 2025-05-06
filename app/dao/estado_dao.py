from functools import cache
import time
from typing import List, Literal
from psycopg2 import Error
from psycopg2.extras import DictCursor

from .dao_utils import build_where
from ..database.database_connection import get_connection
from ..utils.logging_config import app_logger, error_logger

@cache
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
                tabela_view = f"mv_{tipo}ortacao_estado_anual"
                where_conditions = []
                params = []

                if anos:
                    where_conditions.append("m.ano IN %s")
                    params.append(anos)

                if ncm:
                    where_conditions.append("m.id_produto IN %s")
                    params.append(ncm)

                if paises:
                    where_conditions.append("m.id_pais IN %s")
                    params.append(paises)

                if meses:
                    app_logger.warning("Filtro por meses ignorado - não disponível nas views materializadas")

                if vias or urfs:
                    app_logger.warning("Filtros por vias ou URFs ignorados - não disponíveis nas views materializadas")

                where_sql = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

                query = f"""
                    SELECT 
                        e.id_estado,
                        e.sigla AS sigla_estado,
                        e.nome AS nome_estado,
                        SUM(m.valor_fob_total) AS total_valor_fob,
                        SUM(m.kg_liquido_total) AS total_kg_liquido,
                        CASE 
                            WHEN SUM(m.kg_liquido_total) = 0 THEN 0
                            ELSE CAST(SUM(m.valor_fob_total) / SUM(m.kg_liquido_total) AS DECIMAL(15,2))
                        END AS total_valor_agregado,
                        SUM(m.quantidade_total) AS total_registros
                    FROM {tabela_view} m
                    JOIN estado e ON m.id_estado = e.id_estado
                    {where_sql}
                    GROUP BY e.id_estado, e.sigla, e.nome
                    ORDER BY total_{crit} {'ASC' if cresc else 'DESC'}
                    LIMIT %s
                """

                params.append(qtd)

                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
                
    except Error as e:
        error_logger.error(f"Erro ao buscar ranking dos estados: {str(e)}")
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