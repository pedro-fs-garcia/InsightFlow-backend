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
        estados: tuple[int, ...] | None = None
)-> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                where_statement = build_where(anos=anos, estados=estados)
                sh4_str = ', '.join([f"'{s}'" for s in sh4])
                if where_statement.startswith("WHERE"):
                    where_statement += f"AND id_sh4 IN ({sh4_str})"
                else:
                    where_statement = f"WHERE id_sh4 IN ({sh4_str})"

                query = f"""
                    SELECT 
                        COALESCE(SUM(valor_fob_exp), 0) AS total_valor_fob_exp,
                        COALESCE(SUM(valor_fob_imp), 0) AS total_valor_fob_imp
                    FROM mv_vlfob_setores
                    {where_statement}
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
    

def busca_sh4_info(sh4:str):
    try: 
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query = "SELECT id_sh4, descricao FROM sh4 WHERE id_sh4 = %s"
                cur.execute(query, (sh4,))
                info = dict(cur.fetchone())
                query = "SELECT p.id_ncm FROM produto p JOIN sh4 ON p.id_sh4 = sh4.id_sh4 WHERE p.id_sh4 = %s"
                cur.execute(query, (sh4,))
                ncms = [item[0] for item in cur.fetchall()]
                info['ncm'] = ncms
                print(info)
                return info
    except (Error, OperationalError) as e:
        error_logger.error(f"Erro ao buscar informações do sh4 {sh4}. Erro: {str(e)}")
        return None
    

def pesquisa_sh4_por_nome(nome:str) -> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query = """
                    SELECT id_sh4, descricao
                    FROM sh4
                    WHERE unaccent(descricao) ILIKE unaccent (%s)
                    ORDER BY
                        CASE
                            WHEN unaccent(descricao) ILIKE unaccent(%s) THEN 0
                            ELSE 1
                        END,
                        unaccent(descricao) ASC
                """
                cur.execute(query, (f"%{nome}%", f"{nome}%"))
                response = [dict(row) for row in cur.fetchall()]
                app_logger.info(f"Pesquisa sh4 por nome '{nome}' executada.")
                return response
    except Error as e:
        error_logger.error(f"Erro ao pesquisar sh4 pelo nome '{nome}': {str(e)}")
        return None


def busca_todos_ncm():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT id_sh4, descricao FROM sh4 ORDER BY id_sh4")
                return [dict(row) for row in cur.fetchall()]
    except Error as e:
        error_logger.error(f"Erro ao buscar todos sh4 no banco de dados: {str(e)}")
        return None


@cache
def ranking_sh4(
    tipo:str, 
    qtd:int=10, 
    anos:List[int]=None, 
    estados:List[int]=None, 
    paises:List[int] = None,
    crit: Literal['valor_fob', 'kg_liquido', 'valor_agregado'] = 'valor_fob',
    cresc: Literal[1, 0] = 0
) -> List[dict]:
    where_statement = build_where(anos=anos, estados=estados, paises=paises)
    query = f"""
        SELECT s.id_sh4, s.descricao as sh4_descricao,
            SUM(e.valor_fob) as total_valor_fob,
            SUM(e.kg_liquido) as total_kg_liquido,
            CAST(SUM(e.valor_fob)/NULLIF(SUM(e.kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado
        FROM {tipo}ortacao_estado e 
        JOIN produto p ON e.id_produto = p.id_ncm
        JOIN sh4 s ON s.id_sh4 = p.id_sh4
        {where_statement}
        GROUP BY s.id_sh4, s.descricao
        ORDER BY total_{crit} {'ASC' if cresc else 'DESC'}
        LIMIT %s
    """
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                inicio = time.time()
                cur.execute(query, (qtd,))
                results = [dict(row) for row in cur.fetchall()]
                fim = time.time()
                tempo = f"Tempo de execução: {fim - inicio:.4f} segundos"
                app_logger.info(f"Ranking de sh4 que foram mais {tipo}ortados. {tempo}")
                return results
    except (Error, OperationalError) as e:
        error_logger.error(f"erro ao buscar ranking de sh4")
        return


@cache
def sh4_hist(
    tipo: Literal['exp', 'imp'], 
    sh4: List[str], 
    paises: List[int] | None = None,
    estados: List[int] | None = None
) -> List[dict]:
    sh4 = [str(s).zfill(4) for s in sh4]
    filtro = f"""sh4.id_sh4 IN ({", ".join(f"'{s}'" for s in sh4)})"""
    
    where_statement = build_where(paises=paises, estados=estados)
    if where_statement: 
        where_statement += f" AND {filtro}"
    else:
        where_statement = f"WHERE {filtro}"

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query = f"""
                    SELECT sh4.id_sh4, sh4.descricao,
                        ano, mes,
                        SUM(valor_fob) as total_valor_fob,
                        SUM(kg_liquido) as total_kg_liquido,
                        CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado
                    FROM produto
                    LEFT JOIN {tipo}ortacao_estado ON {tipo}ortacao_estado.id_produto = produto.id_ncm
                    LEFT JOIN sh4 ON sh4.id_sh4 = produto.id_sh4
                    {where_statement}
                    GROUP BY ano, mes, sh4.id_sh4, sh4.descricao
                """
                inicio = time.time()
                cur.execute(query)
                results = [dict(row) for row in cur.fetchall()]
                fim = time.time()

                app_logger.info(f"Busca de histórico por sh4 {sh4} concluída com sucesso. Tempo: {fim - inicio:.4f} segundos")
                return results
    except Error as e:
        error_logger.error(f'Erro ao buscar histórico para sh4 {sh4} no banco de dados: {str(e)}')
        return None
