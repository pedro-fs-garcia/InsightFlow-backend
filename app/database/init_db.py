from mysql.connector import connect, Error
from .. import config
from .create_tables_script import create_tables_script
from ..utils.logging_config import app_logger, error_logger

configure = {
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "database": config.DB_NAME,
    "port": config.DB_PORT
}

def create_database_if_not_exists():
    conn = connect(
        user=configure.get('user'), 
        password=configure.get('password'), 
        host=configure.get('host'), 
        port=configure.get('port')
    )
    try:
        with conn.cursor() as cur:
            db_name = configure.get('database')
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            app_logger.info('Banco de dados criado ou já existente.')
    except Error as e:
        conn.rollback()
        error_logger.error('Ocorreu um erro ao criar o banco de dados:', e)
    finally:
        if conn: conn.close()


def create_tables_if_not_exist():
    conn = connect(**configure)
    try:
        with conn.cursor() as cur:
            cur.execute(create_tables_script)
            app_logger.info("Tabelas criadas ou já existentes.")
    except Error as e:
        conn.rollback()
        error_logger.error("Erro ao criar tabelas no banco de dados.", e)
    finally:
        if conn:conn.close()

def init_db():
    create_database_if_not_exists()
    create_tables_if_not_exist()