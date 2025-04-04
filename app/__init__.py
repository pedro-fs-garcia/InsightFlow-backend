from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

load_dotenv()

# Conectar ao Redis
# redis_client = redis.Redis(host="localhost", port=6379, db=0)
# Configurar Flask-Limiter para proteção contra brute force
limiter = Limiter(key_func=get_remote_address, 
                #   storage_uri="redis://localhost:6379",  # Usa Redis como armazenamento
                  default_limits=["10 per minute"]
                )

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY",'sua-chave-secreta')

    limiter.init_app(app)

    # from .routes.main_routes import main
    # app.register_blueprint(main)
    from .routes.ncm_routes import ncm
    from .routes.sh_routes import sh
    blueprints = [ncm, sh]
    for b in blueprints:
        app.register_blueprint(b)

    return app