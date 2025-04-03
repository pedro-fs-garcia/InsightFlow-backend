from psycopg2.extensions import connection
from psycopg2 import sql, OperationalError, connect


from .build_database import BuildDatabase
from . import config
from .create_tables_script import create_tables_script
from app.utils.logging_config import app_logger, error_logger

configure = {
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "dbname": config.DB_NAME,
    "port": config.DB_PORT
}

def get_connection(config: dict = configure) -> connection | None:
    try:
        connection = connect(**config)
        app_logger.info("Conexão estabelecida com o banco de dados")
        return connection
    except OperationalError as e:
        error_logger.error("Erro ao estabelecer conexão com banco de dados: %s", str(e))
        return None

def create_database_if_not_exists():
    conn = connect(
        user=configure.get('user'), 
        password=configure.get('password'), 
        host=configure.get('host'), 
        port=configure.get('port'),
        dbname='postgres'  # Conecta ao banco padrão para criar o desejado
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            db_name = configure.get('dbname')
            cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [db_name])
            if not cur.fetchone():
                cur.execute(sql.SQL("CREATE DATABASE {}".format(db_name)))
                app_logger.info("Banco de dados criado.")
            else:
                app_logger.info("Banco de dados já existe.")
    except OperationalError as e:
        error_logger.error("Erro ao criar o banco de dados: %s", str(e))
    finally:
        conn.close()

def create_tables_if_not_exist():
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(create_tables_script)
            conn.commit()
            app_logger.info("Tabelas criadas.")
            builder = BuildDatabase(configure)
            builder.buid_db()
            builder.close_connection()
    except OperationalError as e:
        conn.rollback()
        error_logger.error("Erro ao criar tabelas no banco de dados: %s", str(e))
    finally:
        conn.close()

def init_db():
    create_database_if_not_exists()
    create_tables_if_not_exist()