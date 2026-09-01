import logging
from flask import jsonify, request
from src.config.database import get_connection, init_db
from src.config.settings import settings

logger = logging.getLogger(__name__)

class SystemController:
    @staticmethod
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health"
            }
        }), 200

    @staticmethod
    def health_check():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            
            cursor.execute("SELECT COUNT(*) FROM produtos")
            produtos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            usuarios = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            pedidos = cursor.fetchone()[0]
            conn.close()

            # Sanitizado: NUNCA vaza SECRET_KEY ou senhas
            return jsonify({
                "status": "ok",
                "database": "connected",
                "counts": {
                    "produtos": produtos,
                    "usuarios": usuarios,
                    "pedidos": pedidos
                },
                "versao": "1.0.0",
                "ambiente": "production" if not settings.DEBUG else "development"
            }), 200
        except Exception as e:
            logger.error(f"Erro no health check: {e}")
            return jsonify({"status": "erro", "detalhes": str(e)}), 500

    @staticmethod
    def reset_database():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM itens_pedido")
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM usuarios")
        conn.commit()
        conn.close()
        init_db()
        logger.warning("Banco de dados resetado com sucesso")
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200

    @staticmethod
    def executar_query():
        dados = request.get_json() or {}
        query = dados.get("sql", "").strip()
        if not query:
            return jsonify({"erro": "Query não informada"}), 400

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            if query.upper().startswith("SELECT"):
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
                conn.close()
                return jsonify({"dados": result, "sucesso": True}), 200
            else:
                conn.commit()
                conn.close()
                return jsonify({"mensagem": "Query executada", "sucesso": True}), 200
        except Exception as e:
            conn.close()
            return jsonify({"erro": str(e)}), 500
