from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection
from .. import config
from ..utils.logging_config import app_logger, error_logger


configure = {
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "database": config.DB_NAME,
    "port": config.DB_PORT
}


try:
    pool = MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        **configure
    )
    app_logger.info("Pool de conexões criado com sucesso.")
except Error as e:
    error_logger.error(f"Erro ao criar o pool de conexões: {e}")
    pool = None


# Função para obter conexões do pool
def get_connection() -> PooledMySQLConnection | None:
    if pool:
        try:
            connection = pool.get_connection()
            app_logger.info(f"Conexão obtida do pool para o banco {configure.get('database')}")
            return connection
        except Error as e:
            error_logger.error(f"Erro ao obter conexão do pool: {e}")
    return None