import logging
from flask import request, jsonify
from src.models.usuario_model import UsuarioModel

logger = logging.getLogger(__name__)

class UsuarioController:
    @staticmethod
    def listar_usuarios():
        usuarios = UsuarioModel.get_todos()
        return jsonify({"dados": usuarios, "sucesso": True}), 200

    @staticmethod
    def buscar_usuario(usuario_id):
        usuario = UsuarioModel.get_por_id(usuario_id)
        if usuario:
            return jsonify({"dados": usuario, "sucesso": True}), 200
        return jsonify({"erro": "Usuário não encontrado"}), 404

    @staticmethod
    def criar_usuario():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        nome = dados.get("nome", "").strip()
        email = dados.get("email", "").strip()
        senha = dados.get("senha", "").strip()

        if not nome or not email or not senha:
            return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

        usuario_existente = UsuarioModel.get_por_email(email)
        if usuario_existente:
            return jsonify({"erro": "Email já cadastrado"}), 409

        novo_id = UsuarioModel.criar(nome, email, senha)
        logger.info(f"Usuário criado: {email} (ID: {novo_id})")
        return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201

    @staticmethod
    def login():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        email = dados.get("email", "").strip()
        senha = dados.get("senha", "").strip()

        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        usuario = UsuarioModel.autenticar(email, senha)
        if usuario:
            logger.info(f"Login bem-sucedido: {email}")
            return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
        
        logger.warning(f"Tentativa de login falhou: {email}")
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
