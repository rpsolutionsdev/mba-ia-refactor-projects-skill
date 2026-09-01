import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"erro": "Requisição inválida", "detalhes": str(error), "sucesso": False}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"erro": "Método não permitido", "sucesso": False}), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Erro interno 500: {error}", exc_info=True)
        return jsonify({"erro": "Erro interno no servidor", "sucesso": False}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        logger.error(f"Exceção não tratada: {error}", exc_info=True)
        return jsonify({"erro": "Ocorreu um erro inesperado", "sucesso": False}), 500
