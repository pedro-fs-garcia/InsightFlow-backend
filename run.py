from app import create_app
from dotenv_config import variaveis_de_ambiente

app = create_app()

if __name__ == "__main__":
    variaveis_de_ambiente()
    app.run(host="0.0.0.0", port=5000, debug=True)