import time
from psycopg2 import Error
from psycopg2.extras import DictCursor
from app.database.database_connection import get_connection
from app.utils.logging_config import error_logger, app_logger
from typing import List, Literal

from .dao_utils import build_where

from ..database.database_connection import get_connection
from ..utils.logging_config import app_logger, error_logger


def busca_top_bloco(
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
) -> List[dict] | None:
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)


        where_statement = build_where(anos=anos, estados=estados, meses=meses, vias=vias, urfs=urfs)
        if ncm:
            if where_statement.startswith('WHERE'):
                where_statement += f" AND id_produto IN ({', '.join([str(n) for n in ncm])})"
            else:
                where_statement = f"WHERE id_produto IN ({', '.join([str(n) for n in ncm])})"
        
        if not meses:
            # Se não houver filtro por mês, usar a view materializada
            query = f"""
                SELECT bloco.id_bloco, bloco.nome_bloco,
                    mv_{tipo}ortacao_estado_anual.valor_fob_total as total_valor_fob,
                    mv_{tipo}ortacao_estado_anual.kg_liquido_total as total_kg_liquido,
                    CAST(mv_{tipo}ortacao_estado_anual.valor_fob_total/NULLIF(mv_{tipo}ortacao_estado_anual.kg_liquido_total, 0) AS DECIMAL(15,2)) AS total_valor_agregado,
                    mv_{tipo}ortacao_estado_anual.quantidade_total AS total_registros
                FROM pais
                JOIN bloco ON pais.id_bloco = bloco.id_bloco
                JOIN mv_{tipo}ortacao_estado_anual ON mv_{tipo}ortacao_estado_anual.id_pais = pais.id_pais
                {where_statement}
                GROUP BY bloco.id_bloco, bloco.nome_bloco
                ORDER BY total_{crit} {'ASC' if cresc else 'DESC'}
                LIMIT %s
            """
        else:
            # Usar a tabela original se houver filtro por mês
            query = f"""
                SELECT bloco.id_bloco, bloco.nome_bloco,
                    SUM(valor_fob) as total_valor_fob,
                    SUM(kg_liquido) as total_kg_liquido,
                    CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado,
                    COUNT(*) AS total_registros
                FROM pais
                JOIN bloco ON pais.id_bloco = bloco.id_bloco
                JOIN {tipo}ortacao_estado ON pais.id_pais = {tipo}ortacao_estado.id_pais
                {where_statement}
                GROUP BY bloco.id_bloco, bloco.nome_bloco
                ORDER BY total_{crit} {'ASC' if cresc else 'DESC'}
                LIMIT %s
            """
        inicio = time.time()
        cur.execute(query, (qtd,))
        fim = time.time()
        app_logger.info(f"Tempo de execução da query: {fim - inicio :.4f} segundos")
        return [dict(row) for row in cur.fetchall()]

    except Error as e:
        error_logger.error(f"Erro ao buscar top blocos: {str(e)}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()


def pesquisa_bloco_por_nome(nome: str) -> List[dict] | None:
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)    
        query = """
            SELECT id_bloco, nome_bloco FROM bloco
            WHERE unaccent(nome_bloco) ILIKE unaccent(%s)
            ORDER BY 
                CASE 
                    WHEN nome_bloco ILIKE %s THEN 0
                    ELSE 1
                END,
                    unaccent(nome_bloco) ASC
        """
        cur.execute(query, (f"%{nome}%", f"{nome}%"))
        results = [dict(row) for row in cur.fetchall()]
        app_logger.info(f"pesquisa por blocos com '{nome}' realizada.")
        return results
    except Error as e:
        error_logger.error(f"Erro ao pesquisar blocos por nome no banco de dados: {str(e)}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()


def busca_todos_blocos():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT id_bloco, nome FROM bloco ORDER BY nome ASC")
        results = [dict(row) for row in cur.fetchall()]
        app_logger.info("Todos os blocos buscados com sucesso.")
        return results
    except Error as e:
        error_logger.error(f"Erro ao buscar todos os blocos no banco de dados: {str(e)}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()
