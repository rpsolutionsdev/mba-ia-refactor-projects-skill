import logging
from flask import Flask
from flask_cors import CORS
from src.config.settings import settings
from src.config.database import init_db
from src.routes.produto_routes import produto_bp
from src.routes.usuario_routes import usuario_bp
from src.routes.pedido_routes import pedido_bp
from src.routes.relatorio_routes import relatorio_bp
from src.routes.system_routes import system_bp
from src.middlewares.error_handler import register_error_handlers

def create_app():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    CORS(app)

    # Inicialização do banco de dados
    init_db()

    # Registro de Blueprints (Camada de Roteamento)
    app.register_blueprint(system_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)

    # Middleware de tratamento centralizado de erros
    register_error_handlers(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
