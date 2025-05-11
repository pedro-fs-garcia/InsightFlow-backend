from functools import cache
import time
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
                where_statement = build_where(ncm=ncm, paises=paises, estados=estados, anos=anos, meses=meses, urfs=urfs, vias=vias)
                where_statement = where_statement.replace('produto.id_ncm', 'id_produto')
                if peso:
                    if where_statement.startswith('WHERE'):
                        where_statement += f"AND kg_liquido > {peso}"
                    else:
                        where_statement = f"WHERE kg_liquido > {peso}"
                if paises:
                    where_statement = where_statement.replace('id_pais', 'p.id_pais')
                if estados:
                    where_statement = where_statement.replace('id_estado', 'e.id_estado')
                if vias:
                    where_statement = where_statement.replace('id_modal_transporte', 'v.id_modal_transporte')

                query = f"""
                    SELECT id_transacao, ano, valor_fob, kg_liquido, valor_agregado, 
                        ncm.descricao AS mercadoria,
                        p.nome AS nome_pais, 
                        e.sigla AS sigla_estado, 
                        v.descricao AS transporte,
                        urf.nome AS unidade_receita_federal
                    FROM {tipo}ortacao_estado t 
                    JOIN pais p ON p.id_pais = t.id_pais
                    JOIN estado e ON e.id_estado = t.id_estado
                    JOIN modal_transporte v ON v.id_modal_transporte = t.id_modal_transporte
                    JOIN unidade_receita_federal urf ON urf.id_unidade = t.id_unidade_receita_federal
                    JOIN produto ncm on ncm.id_ncm = t.id_produto
                    {where_statement}
                    ORDER BY t.valor_fob DESC
                    LIMIT %s
                """
                cur.execute(query, (qtd, ))
                res = cur.fetchall()
                return [dict(row) for row in res]
    except (Error, OperationalError) as e:
        error_logger.error(f'Erro ao buscar transações por NCM {ncm} no banco de dados: {str(e)}')
        return None


def busca_por_ncm(
        ncm:List[int],
        anos:List[int] | None = None,
        meses:List[int] | None = None,
        paises:List[int] | None = None,
        vias:List[int] | None = None,
        urfs:List[int] | None = None
    ) -> List[dict]:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                where_statement = build_where(anos=anos, meses=meses, paises=paises, vias=vias, urfs=urfs, ncm=ncm)
                
                # Se não houver filtro por mês, usar a view materializada
                if not meses and not vias and not urfs:
                    if 'ano' in where_statement:
                        where_statement = where_statement.replace('ano', 'mv_exportacao_estado_anual.ano')
                    
                    query = f"""
                        SELECT produto.descricao AS produto_descricao,
                            sh4.descricao AS sh4_descricao,
                            SUM(mv_exportacao_estado_anual.valor_fob_total) AS total_valor_fob_exp,
                            SUM(mv_exportacao_estado_anual.kg_liquido_total) AS total_kg_liquido_exp,
                            CAST(SUM(mv_exportacao_estado_anual.valor_fob_total)/NULLIF(SUM(mv_exportacao_estado_anual.kg_liquido_total), 0) AS DECIMAL(15,2)) AS total_valor_agregado_exp,
                            
                            SUM(mv_importacao_estado_anual.valor_fob_total) AS total_valor_fob_imp,
                            SUM(mv_importacao_estado_anual.kg_liquido_total) AS total_kg_liquido_imp,
                            SUM(mv_importacao_estado_anual.valor_seguro_total) AS total_valor_seguro_imp,
                            SUM(mv_importacao_estado_anual.valor_frete_total) AS total_valor_frete_imp,
                            CAST(SUM(mv_importacao_estado_anual.valor_fob_total)/NULLIF(SUM(mv_importacao_estado_anual.kg_liquido_total), 0) AS DECIMAL(15,2)) AS total_valor_agregado_imp            
                        FROM produto 
                        LEFT JOIN mv_exportacao_estado_anual ON mv_exportacao_estado_anual.id_produto = produto.id_ncm
                        LEFT JOIN mv_importacao_estado_anual ON mv_importacao_estado_anual.id_produto = produto.id_ncm
                        JOIN sh4 ON sh4.id_sh4 = produto.id_sh4
                        {where_statement}
                        GROUP BY produto.id_ncm, sh4.id_sh4
                    """
                else:
                    # Usar a tabela original se houver filtro por mês
                    if 'ano' in where_statement:
                        where_statement = where_statement.replace('ano', 'exportacao_estado.ano')
                    if 'mes' in where_statement:
                        where_statement = where_statement.replace('mes', 'exportacao_estado.mes')
                    if 'id_modal_transporte' in where_statement:
                        where_statement = where_statement.replace('id_modal_transporte', 'exportacao_estado.id_modal_transporte')
                    if 'id_unidade_receita_federal' in where_statement:
                        where_statement = where_statement.replace('id_unidade_receita_federal', 'exportacao_estado.id_unidade_receita_federal')
                    print(where_statement)
                    query = f"""
                        SELECT produto.descricao AS produto_descricao,
                            sh4.descricao AS sh4_descricao,
                            SUM(exportacao_estado.valor_fob) AS total_valor_fob_exp,
                            SUM(exportacao_estado.kg_liquido) AS total_kg_liquido_exp,
                            CAST(SUM(exportacao_estado.valor_fob)/NULLIF(SUM(exportacao_estado.kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado_exp,
                            
                            SUM(importacao_estado.valor_fob) AS total_valor_fob_imp,
                            SUM(importacao_estado.kg_liquido) AS total_kg_liquido_imp,
                            SUM(importacao_estado.valor_seguro) AS total_valor_seguro_imp,
                            SUM(importacao_estado.valor_frete) AS total_valor_frete_imp,
                            CAST(SUM(importacao_estado.valor_fob)/NULLIF(SUM(importacao_estado.kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado_imp            
                        FROM produto 
                        LEFT JOIN exportacao_estado ON exportacao_estado.id_produto = produto.id_ncm
                        LEFT JOIN importacao_estado ON importacao_estado.id_produto = produto.id_ncm
                        JOIN sh4 ON sh4.id_sh4 = produto.id_sh4
                        {where_statement}
                        GROUP BY produto.id_ncm, sh4.id_sh4
                    """
                inicio = time.time()
                cur.execute(query)  
                results = [dict(row)for row in cur.fetchall()]
                fim = time.time()

                tempo = f"Tempo de execução: {fim - inicio:.4f} segundos"
                app_logger.info(f"Busca por ncm {ncm} concluída com sucesso. {tempo}")
                return results
    
    except (Error, OperationalError) as e:
        error_logger.error(f'Erro ao buscar NCM {ncm} no banco de dados: {str(e)}')
        return None


@cache
def busca_ncm_hist(
        tipo:Literal['exp', 'imp'], 
        ncm:List[int], 
        anos:List[int] | None = None,
        meses:List[int] | None = None,
        paises: List[int] | None = None,
        estados: List[int] | None = None,
        vias: List[int] | None = None,
        urfs: List[int] | None = None
    ) -> List[dict]:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                where_statement = build_where(anos=anos, meses=meses, paises=paises, estados=estados, vias=vias, urfs=urfs, ncm=ncm)
                query = f"""
                    SELECT produto.id_ncm, produto.descricao,
                        ano, mes,
                        SUM(valor_fob) as total_valor_fob,
                        SUM(kg_liquido) as total_kg_liquido,
                        CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado,
                        COUNT(*) AS total_registros
                    FROM produto
                    LEFT JOIN {tipo}ortacao_estado ON {tipo}ortacao_estado.id_produto = produto.id_ncm
                    {where_statement}
                    GROUP BY produto.id_ncm, ano, mes
                    ORDER BY ano, mes
                """
                inicio = time.time()
                cur.execute(query)  
                results = [dict(row)for row in cur.fetchall()]
                fim = time.time()

                tempo = f"Tempo de execução: {fim - inicio:.4f} segundos"
                app_logger.info(f"Busca por ncm {ncm} concluída com sucesso. {tempo}")
                return results
    except Error as e:
        error_logger.error(f'Erro ao buscar NCM {ncm} no banco de dados: {str(e)}')
        return None

    
@cache    
def busca_top_ncm(
        tipo: Literal['exp', 'imp'],
        qtd: int = 10, 
        anos: tuple[int, ...] = None, 
        meses: tuple[int, ...] | None = None,
        paises: tuple[int, ...] | None = None,
        estados: tuple[int, ...] | None = None,
        vias: tuple[int, ...] | None = None,
        urfs: tuple[int, ...] | None = None,
        crit: Literal['kg_liquido', 'valor_fob', 'valor_agregado', 'registros'] = 'valor_fob',
        cresc: Literal[1, 0] = 0
    ) -> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                app_logger.info("Busca por top NCM iniciada.")

                where_statement = build_where(anos=anos, meses=meses, paises=paises, estados=estados, vias=vias, urfs=urfs)
                
                # Se não houver filtro por mês, usar a view materializada
                if not meses and not vias and not urfs:
                    if 'ano' in where_statement:
                        where_statement = where_statement.replace('ano', f'mv_{tipo}ortacao_estado_anual.ano')
                    
                    query = f"""
                        SELECT mv_{tipo}ortacao_estado_anual.id_produto AS ncm, 
                            produto.descricao AS produto_descricao,
                            sh4.descricao AS sh4_descricao,
                            SUM(mv_{tipo}ortacao_estado_anual.valor_fob_total) as total_valor_fob,
                            SUM(mv_{tipo}ortacao_estado_anual.kg_liquido_total) as total_kg_liquido,
                            CAST(SUM(mv_{tipo}ortacao_estado_anual.valor_fob_total)/NULLIF(SUM(mv_{tipo}ortacao_estado_anual.kg_liquido_total), 0) AS DECIMAL(15,2)) AS total_valor_agregado,
                            SUM(mv_{tipo}ortacao_estado_anual.quantidade_total) AS total_registros
                        FROM mv_{tipo}ortacao_estado_anual
                        JOIN produto ON produto.id_ncm = mv_{tipo}ortacao_estado_anual.id_produto
                        JOIN sh4 ON produto.id_sh4 = sh4.id_sh4 
                        {where_statement}
                        GROUP BY mv_{tipo}ortacao_estado_anual.id_produto, 
                            produto.descricao, 
                            sh4.descricao
                        ORDER BY total_{crit} {'ASC' if cresc else 'DESC'}
                        LIMIT %s
                    """
                    print(query)
                else:
                    # Usar a tabela original se houver filtro por mês
                    if 'ano' in where_statement:
                        where_statement = where_statement.replace('ano', f'{tipo}ortacao_estado.ano')
                    
                    query = f"""
                        SELECT id_produto AS ncm, 
                            produto.descricao AS produto_descricao,
                            sh4.descricao AS sh4_descricao,
                            SUM(valor_fob) as total_valor_fob,
                            SUM(kg_liquido) as total_kg_liquido,
                            CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado,
                            COUNT(*) AS total_registros
                        FROM {tipo}ortacao_estado
                        JOIN produto ON produto.id_ncm = {tipo}ortacao_estado.id_produto
                        JOIN sh4 ON produto.id_sh4 = sh4.id_sh4 
                        {where_statement}
                        GROUP BY id_produto, produto.descricao, sh4.descricao
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
        error_logger.error(f'Erro ao buscar top NCM no banco de dados: {str(e)}')
        return None


def pesquisa_ncm_por_nome(nome:str) -> List[dict] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query = """
                    SELECT id_ncm, descricao
                    FROM produto
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
                app_logger.info(f"Pesquisa ncm por nome '{nome}' executada.")
                return response
    except Error as e:
        error_logger.error(f"Erro ao pesquisar ncm pelo nome '{nome}': {str(e)}")
        return None


def busca_todos_ncm():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT id_ncm, descricao FROM produto ORDER BY id_ncm")
                return [dict(row) for row in cur.fetchall()]
    except Error as e:
        error_logger.error(f"Erro ao buscar todos ncm no banco de dados: {str(e)}")
        return None
        