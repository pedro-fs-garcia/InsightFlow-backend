from flask import Blueprint


main = Blueprint ('main', __name__)


@main.route('/', methods=['GET'])
def main_function():
    return

from .ncm_routes import ncm_bp
from .bloco_routes import bloco_bp
from .pais_routes import pais_bp
from .sh_routes import sh_bp
from .bc_routes import balanca_comercial_bp

all_blueprints = [
    main, 
    ncm_bp, 
    pais_bp, 
    bloco_bp, 
    sh_bp, 
    balanca_comercial_bp
]