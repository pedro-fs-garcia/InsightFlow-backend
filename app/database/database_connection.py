from contextlib import contextmanager
from typing import Generator
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extensions import connection as _connection
from psycopg2 import OperationalError

from .. import config
from ..utils.logging_config import app_logger, error_logger


configure = {
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "dbname": config.DB_NAME,
    "port": config.DB_PORT
}

# Criar pool de conexões
try:
    pool = SimpleConnectionPool(1, 5,
                                user=configure["user"],
                                password=configure["password"],
                                host=configure["host"],
                                port=configure["port"],
                                dbname=configure["dbname"])
    app_logger.info("Pool de conexões criado com sucesso.")
except OperationalError as e:
    error_logger.error(f"Erro ao criar o pool de conexões: {e}")
    pool = None


@contextmanager
def get_connection() -> Generator[_connection, None, None]:
    """Obtém uma conexão do pool."""
    conn = None
    try:
        conn = pool.getconn()
        app_logger.info(f"Conexão obtida do pool para o banco {configure.get('dbname')}")
        yield conn
    except OperationalError as e:
        error_logger.error(f"Erro ao obter conexão do pool: {e}")
        raise  # ← Propaga o erro para ser tratado no `try` de quem chamou
    finally:
        if conn:
            pool.putconn(conn)
            app_logger.info("Conexão devolvida ao pool.")