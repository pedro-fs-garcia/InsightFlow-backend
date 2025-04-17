from functools import cache
import time
from typing import List, Literal
from psycopg2 import Error, OperationalError
from psycopg2.extras import DictCursor
from app.dao.dao_utils import build_where
from app.database.database_connection import get_connection
from app.utils.logging_config import app_logger, error_logger


def busca_todos_sh4() -> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor)as cur:
                cur.execute("SELECT sh4.id_sh4, sh4.descricao FROM sh4 ORDER BY id_sh4")
                return [dict(row) for row in cur.fetchall()]
    except Error as e:
        error_logger.error(f'Erro ao buscar todos sh4 no banco de dados: {str(e)}')
        return None    


def pesquisa_sh4_por_nome(nome:str) -> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor)as cur:
                query = """
                    SELECT id_sh4, descricao FROM sh4
                    WHERE unaccent(descricao) ILIKE unaccent(%s)
                    ORDER BY
                        CASE
                            WHEN unaccent(descricao) ILIKE unaccent(%s) THEN 0
                            ELSE 1
                        END,
                        unaccent(descricao) ASC
                """
                cur.execute(query, (f"%{nome}%", f"{nome}%"))
                return [dict(row) for row in cur.fetchall()]
    except Error as e:
        error_logger.error(f'Erro ao buscar todos sh4 no banco de dados: {str(e)}')
        return None    


def busca_top_sh4_por_municipio(
    tipo: Literal['exp', 'imp'],
    qtd: int = 10, 
    anos: List[int] = None, 
    meses: List[int] | None = None,
    paises: List[int] | None = None,
    municipios: List[int] | None = None,
    crit: Literal['kg_liquido', 'valor_fob', 'valor_agregado', 'registros'] = 'valor_fob',
    cresc: Literal[1, 0] = 0 
) -> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                app_logger.info("Busca por top NCM iniciada.")
                where_statement = build_where(anos=anos, meses=meses, paises=paises, municipios=municipios)

                if crit == 'registros':
                    having_statement = ""
                elif crit == 'valor_agregado':
                    having_statement = "HAVING SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) IS NOT NULL"
                else:
                    having_statement = f"HAVING SUM({crit}) > 0"
                
                query = f"""
                    SELECT {tipo}ortacao_municipio.id_sh4 AS sh4, 
                        sh4.descricao AS sh4_descricao,
                        SUM(valor_fob) as total_valor_fob,
                        SUM(kg_liquido) as total_kg_liquido,
                        CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado,
                        COUNT(*) AS total_registros
                    FROM {tipo}ortacao_municipio
                    JOIN sh4 ON {tipo}ortacao_municipio.id_sh4 = sh4.id_sh4 
                    {where_statement}
                    GROUP BY {tipo}ortacao_municipio.id_sh4, sh4.descricao
                    {having_statement}
                    ORDER BY total_{crit} {'ASC' if cresc else 'DESC'}
                    LIMIT %s
                """
                inicio = time.time()
                cur.execute(query, (qtd,))
                results = [dict(row)for row in cur.fetchall()]
                fim = time.time()
                tempo = f"Tempo de execução: {fim - inicio:.4f} segundos"
                app_logger.info(f"Top {qtd} NCM mais {tipo}ortados para os anos {anos} classificados por {crit}. {tempo}")
            return results

    except Error as e:
        error_logger.error(f'Erro ao buscar top sh4 por município no banco de dados: {str(e)}')
        return None    
    

@cache
def busca_vlfob_sh4(
        sh4: tuple[str, ...],
        anos: tuple[int, ...] | None = None,
        paises: tuple[int, ...] | None = None,
        estados: tuple[int, ...] | None = None
)-> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                where_statement = build_where(anos=anos, paises=paises, estados=estados)
                sh4_str = ', '.join([f"'{s}'" for s in sh4])
                if where_statement.startswith("WHERE"):
                    where_statement += f"AND s.id_sh4 IN ({sh4_str})"
                else:
                    where_statement = f"WHERE s.id_sh4 IN ({sh4_str})"

                query = f"""
                    WITH exportacoes AS (
                        SELECT 
                            p.id_sh4,
                            SUM(e.valor_fob) AS total_valor_fob_exp
                        FROM produto p
                        JOIN sh4 s ON s.id_sh4 = p.id_sh4
                        JOIN exportacao_estado e ON e.id_produto = p.id_ncm
                        {where_statement}
                        GROUP BY p.id_sh4
                    ),
                    importacoes AS (
                        SELECT 
                            p.id_sh4,
                            SUM(i.valor_fob) AS total_valor_fob_imp
                        FROM produto p
                        JOIN sh4 s ON s.id_sh4 = p.id_sh4
                        JOIN importacao_estado i ON i.id_produto = p.id_ncm
                        {where_statement}
                        GROUP BY p.id_sh4
                    )
                    SELECT 
                        COALESCE(SUM(e.total_valor_fob_exp), 0) AS total_valor_fob_exp,
                        COALESCE(SUM(i.total_valor_fob_imp), 0) AS total_valor_fob_imp
                    FROM exportacoes e
                    FULL OUTER JOIN importacoes i ON e.id_sh4 = i.id_sh4
                """
                inicio = time.time()
                cur.execute(query)
                res = cur.fetchone()
                fim = time.time()
                tempo = f"Tempo de execução: {fim-inicio :.4f} seg"
                app_logger.info(f"Busca de vl_fob por sh4 {sh4} realizada com sucesso. {tempo}")
                return [dict(res)]
    except (Error, OperationalError) as e:
        error_logger.error(f"Erro ao buscar valores por sh4 {sh4}. Erro: {str(e)}")
        return None