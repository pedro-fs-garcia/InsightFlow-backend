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

        # Se não houver filtro por mês, usar a view materializada
        if not meses:
            
            query = f"""
                SELECT pais.id_pais,
                    pais.nome AS nome_pais,
                    mv_{tipo}ortacao_estado_anual.valor_fob_total as total_valor_fob,
                    mv_{tipo}ortacao_estado_anual.kg_liquido_total as total_kg_liquido,
                    CAST(mv_{tipo}ortacao_estado_anual.valor_fob_total/NULLIF(mv_{tipo}ortacao_estado_anual.kg_liquido_total, 0) AS DECIMAL(15,2)) AS total_valor_agregado,
                    mv_{tipo}ortacao_estado_anual.quantidade_total AS total_registros
                FROM pais
                JOIN mv_{tipo}ortacao_estado_anual ON mv_{tipo}ortacao_estado_anual.id_pais = pais.id_pais
                {where_statement}
                GROUP BY pais.id_pais, pais.nome
                ORDER BY total_{crit} {'ASC' if cresc else 'DESC'}
                LIMIT %s
            """
        else:
            # Usar a tabela original se houver filtro por mês
            query = f"""
                SELECT pais.id_pais,
                    pais.nome AS nome_pais,
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


def busca_pais_hist(
        tipo:Literal['exp', 'imp'],
        paises: List[int],
        anos: List[int] | None = None,
        meses: List[int] | None = None,
        estados: List[int] | None = None,
        vias: List[int] | None = None,
        urfs: List[int] | None = None,
        ncm: List[int] | None = None,
) -> List[dict] | None:
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        where_statement = build_where(anos=anos, meses=meses, paises=paises, estados=estados, vias=vias, urfs=urfs, ncm=ncm)
        where_statement = where_statement.replace('id_pais', 'pais.id_pais')
        if ncm:
            where_statement += f" AND id_produto IN ({', '.join([str(n) for n in ncm])})"

        query = f"""
            SELECT pais.id_pais, pais.nome AS nome_pais,
                ano, mes,
                bloco.nome_bloco, 
                SUM(kg_liquido) as kg_liquido_total_{tipo},
                SUM(valor_fob) as valor_fob_total_{tipo},
                CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS valor_agregado_total_{tipo},
                COUNT(*) AS total_registros

            FROM pais
            LEFT JOIN bloco ON pais.id_bloco = bloco.id_bloco
            LEFT JOIN {tipo}ortacao_estado ON pais.id_pais = {tipo}ortacao_estado.id_pais
            {where_statement}
            GROUP BY pais.id_pais, ano, mes, bloco.nome_bloco
            ORDER BY ano, mes
        """

        inicio = time.time()
        cur.execute(query)
        results = [dict(row) for row in cur.fetchall()]
        fim = time.time()
        tempo = f"Tempo de execução: {fim - inicio:.4f} segundos"
        app_logger.info(f"Histórico dos países {paises}. {tempo}")
        return results

    except Error as e:
        error_logger.error(f"Erro ao buscar o histórico de países no banco de dados: {str(e)}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()


def pesquisa_pais_por_nome(nome:str) -> List[dict] | None:
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT id_pais, nome FROM pais
            WHERE unaccent(nome) ILIKE unaccent(%s)
            ORDER BY 
                CASE 
                    WHEN nome ILIKE %s THEN 0
                    ELSE 1
                END,
                unaccent(nome) ASC
        """
        cur.execute(query, (f"%{nome}%", f"{nome}%"))
        
        results = [dict(row) for row in cur.fetchall()]
        app_logger.info(f"pesquisa por paises com '{nome}' realizada.")
        return results

    except Error as e:
        error_logger.error(f"Erro ao pesquisar países por nome no banco de dados: {str(e)}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()


def busca_todos_paises():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT id_pais, nome FROM pais ORDER BY nome ASC")
        results = [dict(row) for row in cur.fetchall()]
        app_logger.info("Todos os países buscados com sucesso.")
        return results
    except Error as e:
        error_logger.error("Erro ao buscar todos os países.")
        return None
    finally:
        if cur:cur.close()
        if conn:conn.close()