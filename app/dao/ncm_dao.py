import time
from typing import List, Literal
import psycopg2
from psycopg2.extras import DictCursor
from app.database.database_connection import get_connection
from app.utils.logging_config import app_logger, error_logger

def build_where(anos=None, meses=None, paises=None, estados=None, vias=None):
    filtros = []

    if anos:
        anos = [str(ano) for ano in anos]
        filtros.append(f"ano IN ({', '.join(anos)})")

    if meses:
        meses = [str(mes) for mes in meses]
        filtros.append(f"mes IN ({', '.join(meses)})")

    if paises:
        paises = [str(pais) for pais in paises]
        filtros.append(f"id_pais IN ({', '.join(paises)})")

    if estados:
        estados = [str(estado) for estado in estados]
        filtros.append(f"id_estado IN ({', '.join(estados)})")
    
    if vias:
        vias = [str(via) for via in vias]
        filtros.append(f"id_modal_transporte IN ({', '.join(vias)})")

    return f"WHERE {' AND '.join(filtros)}" if filtros else ""

def busca_top_ncm(
                tipo: Literal['exp', 'imp'],
                qtd: int = 10, 
                anos: List[int] = None, 
                meses: List[int] | None = None,
                paises: List[int] | None = None,
                estados: List[int] | None = None,
                vias: List[int] | None = None,
                crit: Literal['kg_liquido', 'valor_fob', 'valor_agregado', 'registros'] = 'valor_fob') -> dict | None:
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            app_logger.info("Busca por top NCM iniciada.")
            where_statement = build_where(anos, meses, paises, estados, vias)
            
            if crit == 'registros':
                sql = f"""
                    SELECT id_produto AS ncm, 
                        produto.descricao AS produto_descricao,
                        COUNT(*) AS registros
                    FROM {tipo}ortacao_estado
                    JOIN produto ON produto.id_ncm = {tipo}ortacao_estado.id_produto
                    {where_statement}
                    GROUP BY id_produto, produto.descricao
                    ORDER BY registros DESC
                    LIMIT %s
                """
            elif crit == 'valor_agregado':
                sql = f"""
                    SELECT id_produto AS ncm, 
                        produto.descricao AS produto_descricao, 
                        CAST(SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) AS DECIMAL(15,2)) AS total_valor_agregado
                    FROM {tipo}ortacao_estado
                    JOIN produto ON produto.id_ncm = {tipo}ortacao_estado.id_produto
                    {where_statement}
                    GROUP BY id_produto, produto.descricao
                    HAVING SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) IS NOT NULL
                    ORDER BY total_valor_agregado DESC
                    LIMIT %s
                """
            else:
                sql = f"""
                    SELECT id_produto AS ncm, 
                        produto.descricao AS produto_descricao, 
                        SUM({crit}) AS total_{crit}
                    FROM {tipo}ortacao_estado
                    JOIN produto ON produto.id_ncm = {tipo}ortacao_estado.id_produto
                    {where_statement}
                    GROUP BY id_produto, produto.descricao
                    HAVING SUM({crit}) > 0
                    ORDER BY total_{crit} DESC
                    LIMIT %s
                """
            
            inicio = time.time()
            cur.execute(sql, (qtd,))
            results = cur.fetchall()
            fim = time.time()
            tempo = f"Tempo de execução: {fim - inicio:.4f} segundos"
            app_logger.info(f"Top {qtd} NCM mais {tipo}ortados para os anos {anos} classificados por {crit}, buscados com sucesso. {tempo}")
            
        return results

    except psycopg2.Error as e:
        error_logger.error(f'Erro ao buscar top NCM no banco de dados: {str(e)}')
        return None
    
    finally:
        if conn:conn.close()
