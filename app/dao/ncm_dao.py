import time
from typing import List, Literal
from psycopg2 import Error
from psycopg2.extras import DictCursor
from app.dao.dao_utils import build_where
from app.database.database_connection import get_connection
from app.utils.logging_config import app_logger, error_logger


def busca_por_ncm(ncm:int) -> List[dict]:
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        query = 'SELECT * FROM produto WHERE id_ncm = %s'
        
        inicio = time.time()
        cur.execute(query, (ncm,))  
        results = [dict(row)for row in cur.fetchall()]
        fim = time.time()

        tempo = f"Tempo de execução: {fim - inicio:.4f} segundos"
        app_logger.info(f"Busca por ncm {ncm} concluída com sucesso. {tempo}")
        return results
    
    except Error as e:
        error_logger.error(f'Erro ao buscar NCM {ncm} no banco de dados: {str(e)}')
        return None
    finally:
        if conn:conn.close()

    

def busca_top_ncm(
        tipo: Literal['exp', 'imp'],
        qtd: int = 10, 
        anos: List[int] = None, 
        meses: List[int] | None = None,
        paises: List[int] | None = None,
        estados: List[int] | None = None,
        vias: List[int] | None = None,
        urfs: List[int] | None = None,
        crit: Literal['kg_liquido', 'valor_fob', 'valor_agregado', 'registros'] = 'valor_fob'
    ) -> List[dict] | None:
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            app_logger.info("Busca por top NCM iniciada.")
            where_statement = build_where(anos=anos, meses=meses, paises=paises, estados=estados, vias=vias, urfs=urfs)

            if crit == 'registros':
                having_statement = ""
            elif crit == 'valor_agregado':
                having_statement = "HAVING SUM(valor_fob)/NULLIF(SUM(kg_liquido), 0) IS NOT NULL"
            else:
                having_statement = f"HAVING SUM({crit}) > 0"
            
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
                {having_statement}
                ORDER BY total_{crit} DESC
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
    finally:
        if conn:conn.close()
