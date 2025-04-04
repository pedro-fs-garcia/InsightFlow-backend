import time
from typing import List, Literal
from psycopg2 import Error
from psycopg2.extras import DictCursor

from .dao_utils import build_where

from ..database.database_connection import get_connection
from ..utils.logging_config import app_logger, error_logger


def busca_top_pais(
        tipo: Literal['exp', 'imp'],
        qtd: int = 10, 
        anos: List[int] = None, 
        meses: List[int] | None = None,
        ncm: List[int] | None = None,
        estados: List[int] | None = None,
        vias: List[int] | None = None,
        urfs: List[int] | None = None,
        crit: Literal['kg_liquido', 'valor_fob', 'valor_agregado', 'registros'] = 'valor_fob',
        cresc: Literal[1, 0] = 0
) -> List[dict]:
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        where_statement = build_where(anos=anos, meses=meses, ncm=ncm, estados=estados, vias=vias,urfs=urfs)
        query = f"""
            SELECT pais.id_pais,
                pais.nome AS pais_nome,
                SUM(valor_fob) as total_valor_fob,
                SUM(kg_liquido) as total_kg_liquido,
                CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado,
                COUNT(*) AS total_registros
            FROM {tipo}ortacao_estado 
            JOIN pais ON {tipo}ortacao_estado.id_pais = pais.id_pais
            {where_statement}
            GROUP BY pais.id_pais, pais.nome
            ORDER BY total_{crit} {'ASC' if cresc else 'DESC'}
            LIMIT %s
        """
        inicio = time.time()
        cur.execute(query, (qtd,))
        results = [dict(row) for row in cur.fetchall()]
        fim = time.time()
        tempo = f"Tempo de execução: {fim - inicio:.4f} segundos"
        app_logger.info(f"Ranking de países que mais {tipo}ortam. {tempo}")
        return results

    except Error as e:
        error_logger.error(f'Erro ao buscar top NCM no banco de dados: {str(e)}')
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()