import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Requisição inválida', 'detalhes': str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Erro interno: {error}", exc_info=True)
        return jsonify({'error': 'Erro interno no servidor'}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        logger.error(f"Exceção não tratada: {error}", exc_info=True)
        return jsonify({'error': 'Ocorreu um erro inesperado'}), 500
