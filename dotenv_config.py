import os


def variaveis_de_ambiente() -> None:
    print("\n * Configurando variáveis de ambiente...")
    if os.path.exists(".env"):
        print(" * Arquivo .env já existe. Nenhuma alteração foi feita.\n")
        return
    
    DB_USER = input("Insira o nome de usuário do banco de dados: ")
    DB_PASSWORD = input("Insira a senha do banco de dados: ")
    DB_HOST = input("Insira o host do banco de dados (ex: localhost): ")
    DB_NAME = input("Insira o nome do banco de dados: ")
    DB_PORT = input("Insira a porta do banco de dados (3306 para MySQL): ")
    FRONTEND_SERVER=input("Insira o nome do servidor frontend: ")

    env_content = f"""
DB_USER={DB_USER if DB_USER else 'root'}
DB_PASSWORD={DB_PASSWORD if DB_PASSWORD else 'default_password'}
DB_HOST={DB_HOST if DB_HOST else 'localhost'}
DB_NAME={DB_NAME if DB_NAME else 'insightflow'}
DB_PORT={DB_PORT if DB_PORT else '3306'}
BACKEND_SERVER=http://localhost:5000
FRONTEND_SERVER={FRONTEND_SERVER if FRONTEND_SERVER else 'http://localhost:5173'}
        """.strip()

    with open('.env', 'w') as env_file:
        env_file.write(env_content)
    print(" * Arquivo .env criado com sucesso!\n")