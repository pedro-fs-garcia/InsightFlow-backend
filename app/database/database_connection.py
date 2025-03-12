from mysql.connector import connect, Error
from .. import config
from ..utils.logging_config import app_logger, error_logger

configure = {
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "database": config.DB_NAME,
    "port": config.DB_PORT
}

def get_connection():
    try:
        connection = connect(**configure)
        if connection.is_connected():
            app_logger.info(f"Conexão com o banco de dados {configure.get('database')} estabelecida com sucesso")
            return connection
    except Error as e:
        error_logger.error(f"Erro ao estabelecer conexão com o banco de dados {configure.get('database')}")
    return None

def init_db():
    conn = get_connection()