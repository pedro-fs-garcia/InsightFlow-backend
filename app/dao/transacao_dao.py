from typing import List, Literal
from psycopg2 import Error, OperationalError
from psycopg2.extras import DictCursor

from app.dao.dao_utils import build_where
from app.database.database_connection import get_connection
from app.utils.logging_config import app_logger, error_logger

def busca_transacoes_por_ncm(
        ncm: int,
        tipo: Literal['imp', 'exp'],
        qtd: int = 25,
        paises: List[int] = None,
        estados: List[int] = None,
        anos : List[int] = None,
        meses: List[int] = None,
        vias: List[int] = None,
        urfs: List[int] = None,
        peso: int = None
) -> List[dict]:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                where_statement = build_where(paises=paises, estados=estados, anos=anos, meses=meses, urfs=urfs, vias=vias)
                if peso:
                    if where_statement.startswith('WHERE'):
                        where_statement += f"AND kg_liquido > {peso}"
                    else:
                        where_statement = f"WHERE kg_liquido > {peso}"

                query = f"""
                    SELECT id_transacao, ano, id_pais, valor_fob, kg_liquido, valor_agregado 
                    FROM {tipo}ortacao_estado
                    {where_statement}
                    LIMIT %s
                """
                cur.execute(query, (qtd, ))
                res = cur.fetchall()
                app_logger.info(f"Transações buscadas para o ncm: {ncm}")
                return [dict(row) for row in res]
    except (Error, OperationalError) as e:
        error_logger.error(f'Erro ao buscar NCM {ncm} no banco de dados: {str(e)}')
        return None


def busca_transacao_por_id(id_transacao:int, tipo:Literal['imp', 'exp']):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query = f"""
                    SELECT * 
                    FROM {tipo}ortacao_estado
                    WHERE id_transacao = %s
                """
                cur.execute(query, (id_transacao, ))
                res = cur.fetchall()
                app_logger.info(f"Transação buscada para o id: {id_transacao}")
                return [dict(row) for row in res]
    except (Error, OperationalError) as e:
        error_logger.error(f'Erro ao buscar transação de id {id_transacao} no banco de dados: {str(e)}')
        return None