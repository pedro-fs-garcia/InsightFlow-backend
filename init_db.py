from database.init_db import init_db
from dotenv_config import variaveis_de_ambiente


if __name__ == "__main__":
    variaveis_de_ambiente()
    init_db()